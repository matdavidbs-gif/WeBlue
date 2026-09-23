# ============================================================
# WEBLUE - SEGURANÇA DO ADMINISTRADOR
# ============================================================
#
# Este arquivo cuida exclusivamente da segurança
# relacionada aos administradores.
#
# Responsabilidades:
#
# 1. Criar hash da senha do administrador.
# 2. Verificar a senha no momento do login.
# 3. Criar JWT administrativo.
# 4. Validar JWT administrativo.
#
# IMPORTANTE:
#
# O token administrativo utiliza:
#
# "tipo": "admin"
#
# Dessa forma, um token normal de cliente não poderá
# ser utilizado para acessar rotas administrativas.
# ============================================================


# ============================================================
# IMPORTAÇÕES
# ============================================================

from datetime import (
    datetime,
    timedelta,
    timezone,
)

# A Weblue já utiliza PyJWT no security.py dos clientes.
# Portanto, mantemos a mesma biblioteca aqui.
import jwt

# Biblioteca utilizada pelo projeto para gerar
# e verificar hashes de senha.
from pwdlib import PasswordHash

# Configurações gerais da aplicação.
from ..config import settings


# ============================================================
# CONFIGURAÇÃO DO HASH DE SENHA
# ============================================================

# Utiliza a configuração recomendada pelo pwdlib.
#
# É o mesmo padrão utilizado na autenticação dos clientes.
password_hash = PasswordHash.recommended()


# ============================================================
# CONFIGURAÇÃO JWT
# ============================================================

# Chave secreta utilizada para assinar os tokens.
SECRET_KEY = settings.jwt_secret_key

# Algoritmo utilizado para gerar e validar o JWT.
ALGORITHM = settings.jwt_algorithm

# Tempo padrão de duração do token.
TEMPO_TOKEN_MINUTOS = settings.jwt_expire_minutes


# ============================================================
# CRIAR HASH DA SENHA DO ADMINISTRADOR
# ============================================================

def criar_hash_senha_admin(
    senha: str
) -> str:
    """
    Recebe a senha original do administrador
    e gera um hash seguro.

    A senha original nunca deve ser armazenada
    diretamente no banco de dados.
    """

    return password_hash.hash(senha)


# ============================================================
# VERIFICAR SENHA DO ADMINISTRADOR
# ============================================================

def verificar_senha_admin(
    senha: str,
    senha_hash: str
) -> bool:
    """
    Compara a senha informada no login
    com o hash armazenado no banco.

    Retorna:
        True  -> senha correta
        False -> senha incorreta
    """

    try:

        return password_hash.verify(
            senha,
            senha_hash
        )

    except Exception:

        # Caso exista algum problema durante
        # a verificação, o acesso é negado.
        return False


# ============================================================
# CRIAR TOKEN JWT DO ADMINISTRADOR
# ============================================================

def criar_token_admin(
    administrador_id: int
) -> str:
    """
    Cria um JWT exclusivo para o administrador.

    O token contém:

    sub  -> ID do administrador
    tipo -> identifica que é um token administrativo
    iat  -> momento de criação
    exp  -> momento de expiração
    """

    # Data e hora atual em UTC.
    agora = datetime.now(
        timezone.utc
    )


    # Calcula quando o token irá expirar.
    expiracao = agora + timedelta(
        minutes=TEMPO_TOKEN_MINUTOS
    )


    # ========================================================
    # CONTEÚDO DO TOKEN
    # ========================================================

    dados_token = {

        # ID do administrador autenticado.
        "sub": str(administrador_id),

        # Este campo diferencia o JWT administrativo
        # do JWT utilizado pelos clientes.
        "tipo": "admin",

        # Data de criação.
        "iat": agora,

        # Data de expiração.
        "exp": expiracao
    }


    # ========================================================
    # GERAR TOKEN
    # ========================================================

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


    return token


# ============================================================
# VERIFICAR TOKEN JWT DO ADMINISTRADOR
# ============================================================

def verificar_token_admin(
    token: str
) -> int | None:
    """
    Valida um token administrativo.

    Se o token for válido:
        retorna o ID do administrador.

    Se o token for inválido ou expirado:
        retorna None.

    Tokens de clientes também serão recusados,
    porque eles não possuem "tipo": "admin".
    """

    try:

        # ====================================================
        # DECODIFICAR TOKEN
        # ====================================================

        dados_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


        # ====================================================
        # VERIFICAR O TIPO DO TOKEN
        # ====================================================

        tipo_token = dados_token.get(
            "tipo"
        )


        # Somente tokens administrativos
        # podem continuar.
        if tipo_token != "admin":
            return None


        # ====================================================
        # RECUPERAR ID DO ADMINISTRADOR
        # ====================================================

        administrador_id = dados_token.get(
            "sub"
        )


        # O token precisa possuir um ID.
        if administrador_id is None:
            return None


        # ====================================================
        # RETORNAR ID
        # ====================================================

        return int(
            administrador_id
        )


    # ========================================================
    # TOKEN INVÁLIDO OU EXPIRADO
    # ========================================================

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError
    ):

        return None