from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from ..config import settings


password_hash = PasswordHash.recommended()


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


# =========================
# TOKEN DE ACESSO
# =========================

def criar_token_acesso(
    cliente_id: int,
    lembrar: bool = False
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
        "iat": agora,
        "exp": expiracao
    }

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =========================
# VALIDAÇÃO DO TOKEN DE ACESSO
# =========================

def verificar_token_acesso(
    token: str
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
            algorithms=[ALGORITHM]
        )

        # Verifica se é realmente
        # um token de acesso
        tipo_token = dados_token.get("tipo")

        if tipo_token != "acesso":
            return None

        cliente_id = dados_token.get("sub")

        if cliente_id is None:
            return None

        return int(cliente_id)

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError
    ):
        return None


# =========================
# TOKEN DE RECUPERAÇÃO
# =========================

def criar_token_recuperacao(
    email: str
) -> str:
    """
    Cria um token temporário para
    recuperação de senha.
    """

    agora = datetime.now(timezone.utc)

    expiracao = agora + timedelta(
        minutes=15
    )

    dados_token = {
        "sub": email,
        "tipo": "recuperacao_senha",
        "iat": agora,
        "exp": expiracao
    }

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =========================
# VALIDAÇÃO DO TOKEN
# DE RECUPERAÇÃO
# =========================

def verificar_token_recuperacao(
    token: str,
    email: str
) -> bool:
    """
    Verifica se o token de recuperação
    é válido e pertence ao e-mail informado.
    """

    try:

        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email_token = dados_token.get("sub")
        tipo_token = dados_token.get("tipo")

        # Não permite utilizar um token
        # de login para trocar a senha
        if tipo_token != "recuperacao_senha":
            return False

        # O token precisa pertencer
        # ao mesmo e-mail
        if email_token != email:
            return False

        return True

    except jwt.InvalidTokenError:
        return False