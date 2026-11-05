import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy import case, delete
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from ..config import settings
from ..models.cliente_versao_autenticacao import ClienteVersaoAutenticacao
from ..models.rate_limit_window import RateLimitWindow
from ..models.token_revogado import TokenRevogado


password_hash = PasswordHash.recommended()
JWT_ISSUER = "weblue"

REFRESH_TOKEN_DIAS = 7

# =========================
# LIMITAÇÃO DE TENTATIVAS
# =========================


def _get_client_ip(request) -> str:
    """Retorna o IP do cliente, considerando X-Forwarded-For se houver."""

    if request is None:
        return "unknown"

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    client = request.client
    return client.host if client else "unknown"


def _attempt_key(request, identifier: str, prefix: str = "login") -> str:
    """Gera uma chave não reversível para a janela de tentativas."""

    ip = _get_client_ip(request)
    email = (identifier or "").strip().lower()
    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        f"{prefix}:{ip}:{email}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def is_rate_limited(
    request,
    identifier: str,
    database: Session,
    prefix: str = "login",
    max_attempts: int = 5,
    window_seconds: int = 900,
) -> tuple[bool, int]:
    """Retorna (permite, segundos_restantes) para a chave atual."""

    now = datetime.now(UTC).replace(tzinfo=None)
    key = _attempt_key(request, identifier, prefix)
    registro = database.get(RateLimitWindow, key)
    if registro is None:
        return True, 0

    limite = registro.iniciada_em + timedelta(seconds=window_seconds)
    if limite <= now:
        return True, 0

    if registro.tentativas >= max_attempts:
        retry_after = max(1, int((limite - now).total_seconds()))
        return False, retry_after

    return True, 0


def register_failed_attempt(
    request,
    identifier: str,
    database: Session,
    prefix: str = "login",
    window_seconds: int = 900,
) -> None:
    """Registra uma falha de autenticação para a chave atual."""

    now = datetime.now(UTC).replace(tzinfo=None)
    key = _attempt_key(request, identifier, prefix)
    limite = now - timedelta(seconds=window_seconds)
    database.execute(
        delete(RateLimitWindow).where(
            RateLimitWindow.iniciada_em
            <= now - timedelta(seconds=max(window_seconds, 86400))
        )
    )
    database.execute(
        delete(TokenRevogado).where(TokenRevogado.expira_em <= now)
    )
    registro = RateLimitWindow(
        chave=key,
        tentativas=1,
        iniciada_em=now,
    )
    valores_atualizacao = {
        "tentativas": case(
            (RateLimitWindow.iniciada_em <= limite, 1),
            else_=RateLimitWindow.tentativas + 1,
        ),
        "iniciada_em": case(
            (RateLimitWindow.iniciada_em <= limite, now),
            else_=RateLimitWindow.iniciada_em,
        ),
    }

    dialect = database.get_bind().dialect.name
    if dialect == "mysql":
        statement = mysql_insert(RateLimitWindow).values(
            chave=registro.chave,
            tentativas=registro.tentativas,
            iniciada_em=registro.iniciada_em,
        )
        statement = statement.on_duplicate_key_update(**valores_atualizacao)
    elif dialect == "sqlite":
        statement = sqlite_insert(RateLimitWindow).values(
            chave=registro.chave,
            tentativas=registro.tentativas,
            iniciada_em=registro.iniciada_em,
        )
        statement = statement.on_conflict_do_update(
            index_elements=[RateLimitWindow.chave],
            set_=valores_atualizacao,
        )
    else:
        raise RuntimeError(
            f"Banco não suportado para rate limit persistente: {dialect}"
        )

    database.execute(statement)
    database.commit()


def clear_attempts(
    request,
    identifier: str,
    database: Session,
    prefix: str = "login",
) -> None:
    """Limpa tentativas anteriores após sucesso."""

    key = _attempt_key(request, identifier, prefix)
    database.execute(
        delete(RateLimitWindow).where(RateLimitWindow.chave == key)
    )
    database.commit()


# =========================
# CONFIGURAÇÃO JWT
# =========================

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
TEMPO_TOKEN_MINUTOS = settings.jwt_expire_minutes


# =========================
# SENHA
# =========================

def criar_hash_senha(senha: str) -> str:
    """Gera o hash seguro da senha."""

    return password_hash.hash(senha)


def verificar_senha(
    senha: str,
    senha_hash: str
) -> bool:
    """Compara a senha informada com o hash salvo no banco."""

    return password_hash.verify(
        senha,
        senha_hash
    )


def obter_versao_autenticacao_cliente(
    database: Session,
    cliente_id: int,
) -> int:
    estado = database.get(ClienteVersaoAutenticacao, cliente_id)
    return estado.versao if estado is not None else 0


# =========================
# TOKEN DE ACESSO
# =========================

def criar_token_acesso(
    cliente_id: int,
    lembrar: bool = False,
    jti: str | None = None,
    versao_autenticacao: int = 0,
) -> str:
    """Cria um token JWT para o cliente autenticado."""

    agora = datetime.now(timezone.utc)
    if lembrar:
        expiracao = agora + timedelta(days=7)
    else:
        expiracao = agora + timedelta(
            minutes=TEMPO_TOKEN_MINUTOS
        )

    dados_token = {
        "sub": str(cliente_id),
        "tipo": "acesso",
        "iss": JWT_ISSUER,
        "iat": int(agora.timestamp()),
        "nbf": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
        "jti": jti or str(uuid.uuid4()),
        "ver": versao_autenticacao,
    }

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def criar_refresh_token_cliente(
    cliente_id: int,
    versao_autenticacao: int = 0,
) -> tuple[str, str]:
    """Cria um refresh token e seu identificador de sessão."""

    agora = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    expiracao = agora + timedelta(days=REFRESH_TOKEN_DIAS)
    dados_token = {
        "sub": str(cliente_id),
        "tipo": "refresh",
        "iss": JWT_ISSUER,
        "iat": int(agora.timestamp()),
        "nbf": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
        "jti": jti,
        "ver": versao_autenticacao,
    }
    token = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def revogar_token(token: str | None, database: Session) -> None:
    if not token:
        return

    try:
        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            options={"verify_exp": False},
        )
        jti = dados_token.get("jti")
        expiracao = dados_token.get("exp")
        if not isinstance(jti, str) or not isinstance(expiracao, (int, float)):
            return

        expira_em = datetime.fromtimestamp(expiracao, UTC).replace(tzinfo=None)
        if expira_em <= datetime.now(UTC).replace(tzinfo=None):
            return
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError, OverflowError):
        return

    registro = TokenRevogado(jti=jti, expira_em=expira_em)
    dialect = database.get_bind().dialect.name
    if dialect == "mysql":
        statement = mysql_insert(TokenRevogado).values(
            jti=registro.jti,
            expira_em=registro.expira_em,
        ).on_duplicate_key_update(jti=registro.jti)
    elif dialect == "sqlite":
        statement = sqlite_insert(TokenRevogado).values(
            jti=registro.jti,
            expira_em=registro.expira_em,
        ).on_conflict_do_nothing(index_elements=[TokenRevogado.jti])
    else:
        raise RuntimeError(
            f"Banco não suportado para revogação persistente: {dialect}"
        )

    agora = datetime.now(UTC).replace(tzinfo=None)
    database.execute(
        delete(TokenRevogado).where(TokenRevogado.expira_em <= agora)
    )
    database.execute(statement)
    database.commit()


def token_foi_revogado(jti: str | None, database: Session) -> bool:
    if not jti:
        return False

    agora = datetime.now(UTC).replace(tzinfo=None)
    registro = database.get(TokenRevogado, jti)
    if registro is None:
        return False
    if registro.expira_em <= agora:
        database.delete(registro)
        database.commit()
        return False
    return True


# =========================
# VALIDAÇÃO DO TOKEN DE ACESSO
# =========================

def verificar_token_acesso(
    token: str,
    database: Session,
) -> int | None:
    """
    Valida o token de acesso.

    Se for válido, retorna o ID do cliente.
    Caso contrário, retorna None.
    """

    try:
        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "tipo", "iat", "exp", "iss", "nbf", "jti"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            }
        )

        tipo_token = dados_token.get("tipo")
        if tipo_token != "acesso":
            return None

        jti = dados_token.get("jti")
        if token_foi_revogado(jti, database):
            return None

        cliente_id = dados_token.get("sub")
        if cliente_id is None:
            return None

        cliente_id = int(cliente_id)
        if database is not None and int(dados_token.get("ver", 0)) != (
            obter_versao_autenticacao_cliente(database, cliente_id)
        ):
            return None

        return cliente_id

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError
    ):
        return None


def verificar_refresh_token_cliente(
    token: str,
    database: Session,
) -> int | None:
    """Valida refresh token do cliente e rejeita tokens revogados."""

    try:
        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "tipo", "iat", "exp", "iss", "nbf", "jti"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            },
        )

        if dados_token.get("tipo") != "refresh":
            return None

        jti = dados_token.get("jti")
        if token_foi_revogado(jti, database):
            return None

        cliente_id = dados_token.get("sub")
        if cliente_id is None:
            return None

        cliente_id = int(cliente_id)
        if database is not None and int(dados_token.get("ver", 0)) != (
            obter_versao_autenticacao_cliente(database, cliente_id)
        ):
            return None

        return cliente_id
    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        return None
