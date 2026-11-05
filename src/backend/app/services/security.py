import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

import jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from ..config import settings
from ..models.cliente_versao_autenticacao import ClienteVersaoAutenticacao


password_hash = PasswordHash.recommended()
JWT_ISSUER = "weblue"

_LOGIN_ATTEMPTS = defaultdict(deque)
_LOGIN_LOCK = Lock()
_REVOKED_JTIS: set[str] = set()

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
    """Cria uma chave estável para controlar tentativas por IP e identificador."""

    ip = _get_client_ip(request)
    email = (identifier or "").strip().lower()
    return f"{prefix}:{ip}:{email}"


def is_rate_limited(request, identifier: str, prefix: str = "login", max_attempts: int = 5, window_seconds: int = 900):
    """Retorna (permite, segundos_restantes) para a chave atual."""

    now = time.time()
    key = _attempt_key(request, identifier, prefix)

    with _LOGIN_LOCK:
        attempts = _LOGIN_ATTEMPTS[key]
        while attempts and now - attempts[0] > window_seconds:
            attempts.popleft()

        if len(attempts) >= max_attempts:
            oldest = attempts[0]
            retry_after = max(1, int(window_seconds - (now - oldest)))
            return False, retry_after

        return True, 0


def register_failed_attempt(request, identifier: str, prefix: str = "login"):
    """Registra uma falha de autenticação para a chave atual."""

    now = time.time()
    key = _attempt_key(request, identifier, prefix)

    with _LOGIN_LOCK:
        _LOGIN_ATTEMPTS[key].append(now)


def clear_attempts(request, identifier: str, prefix: str = "login"):
    """Limpa tentativas anteriores após sucesso."""

    key = _attempt_key(request, identifier, prefix)

    with _LOGIN_LOCK:
        _LOGIN_ATTEMPTS.pop(key, None)


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


def extrair_jti(token: str) -> str | None:
    """Extrai o identificador do token sem validar assinatura ou expiração."""

    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
            },
        )
        return payload.get("jti")
    except Exception:
        return None


def revogar_token(jti: str | None) -> None:
    if jti:
        _REVOKED_JTIS.add(jti)


def token_foi_revogado(jti: str | None) -> bool:
    return bool(jti and jti in _REVOKED_JTIS)


# =========================
# VALIDAÇÃO DO TOKEN DE ACESSO
# =========================

def verificar_token_acesso(
    token: str,
    database: Session | None = None,
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
        if token_foi_revogado(jti):
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
    database: Session | None = None,
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
        if token_foi_revogado(jti):
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
