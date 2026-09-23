# ============================================================
# WEBLUE - AUTENTICAÇÃO DO ADMINISTRADOR
# ============================================================
#
# Este router é responsável pelo login administrativo.
#
# Fluxo:
#
# 1. Recebe e-mail e senha.
# 2. Procura o administrador no banco.
# 3. Verifica se a conta está ativa.
# 4. Confere a senha com o hash armazenado.
# 5. Gera um JWT exclusivo de administrador.
# 6. Retorna os dados do administrador autenticado.
# ============================================================


# ============================================================
# FASTAPI
# ============================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)


# ============================================================
# SQLALCHEMY
# ============================================================

from sqlalchemy.orm import Session


# ============================================================
# BANCO DE DADOS
# ============================================================
#
# O projeto Weblue utiliza get_database().
#
# Essa função cria uma sessão com o banco MySQL
# e fecha a conexão automaticamente ao final da requisição.
# ============================================================

from ..database import get_database


# ============================================================
# MODEL
# ============================================================

from ..models.administrador import Administrador


# ============================================================
# SCHEMAS
# ============================================================

from ..schemas.administrador import (
    AdministradorLogin,
    AdministradorLoginResposta,
)


# ============================================================
# SEGURANÇA
# ============================================================

from ..services.admin_security import (
    criar_token_admin,
    verificar_senha_admin,
)


# ============================================================
# ROUTER
# ============================================================
#
# Como este router será registrado no api_router,
# que já possui prefix="/api",
#
# a rota final será:
#
# POST /api/admin/auth/login
# ============================================================

router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin - Autenticação"]
)


# ============================================================
# LOGIN DO ADMINISTRADOR
# ============================================================

@router.post(
    "/login",
    response_model=AdministradorLoginResposta,
    status_code=status.HTTP_200_OK,
    summary="Realizar login do administrador"
)
def login_administrador(
    dados: AdministradorLogin,

    # --------------------------------------------------------
    # CORREÇÃO:
    #
    # Antes estava:
    #
    # Depends(get_db)
    #
    # Porém get_db não existe no database.py da Weblue.
    #
    # A função correta é:
    #
    # get_database
    # --------------------------------------------------------

    db: Session = Depends(get_database)
):

    # ========================================================
    # NORMALIZAR E-MAIL
    # ========================================================
    #
    # Remove espaços acidentais e transforma o e-mail
    # em letras minúsculas antes da consulta.
    # ========================================================

    email = dados.email.strip().lower()


    # ========================================================
    # PROCURAR ADMINISTRADOR PELO E-MAIL
    # ========================================================

    administrador = (
        db.query(Administrador)
        .filter(
            Administrador.email == email
        )
        .first()
    )


    # ========================================================
    # ADMINISTRADOR NÃO ENCONTRADO
    # ========================================================
    #
    # A mensagem é propositalmente genérica.
    #
    # Dessa forma não revelamos se determinado
    # e-mail administrativo existe no banco.
    # ========================================================

    if administrador is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )


    # ========================================================
    # VERIFICAR SE A CONTA ESTÁ ATIVA
    # ========================================================

    if not administrador.ativo:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso administrativo desativado."
        )


    # ========================================================
    # VERIFICAR SENHA
    # ========================================================

    senha_correta = verificar_senha_admin(
        dados.senha,
        administrador.senha_hash
    )


    # ========================================================
    # SENHA INCORRETA
    # ========================================================

    if not senha_correta:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )


    # ========================================================
    # GERAR JWT ADMINISTRATIVO
    # ========================================================

    access_token = criar_token_admin(
        administrador.id
    )


    # ========================================================
    # RETORNAR LOGIN
    # ========================================================

    return {
        "mensagem":
            "Login administrativo realizado com sucesso.",

        "access_token":
            access_token,

        "token_type":
            "bearer",

        "administrador":
            administrador
    }