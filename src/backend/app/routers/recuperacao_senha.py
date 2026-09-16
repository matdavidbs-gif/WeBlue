from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente

from ..schemas.recuperacao_senha import (
    SolicitarRecuperacaoRequest,
    RedefinirSenhaRequest
)

from ..services.security import (
    criar_hash_senha,
    criar_token_recuperacao,
    verificar_token_recuperacao
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


# ==========================================
# ETAPA 1 - SOLICITAR RECUPERAÇÃO
# ==========================================

@router.post(
    "/solicitar-recuperacao",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperação de senha"
)
def solicitar_recuperacao(
    dados: SolicitarRecuperacaoRequest,
    database: Session = Depends(get_database)
):

    email = str(dados.email)

    consulta = select(Cliente).where(
        Cliente.email == email
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    token = criar_token_recuperacao(
        cliente.email
    )

    return {
        "mensagem": (
            "Token de recuperação gerado. "
            "O token é válido por 15 minutos."
        ),
        "token_recuperacao": token
    }


# ==========================================
# ETAPA 2 - REDEFINIR SENHA
# ==========================================

@router.post(
    "/redefinir-senha",
    status_code=status.HTTP_200_OK,
    summary="Redefinir senha do cliente"
)
def redefinir_senha(
    dados: RedefinirSenhaRequest,
    database: Session = Depends(get_database)
):

    email = str(dados.email)

    # Verifica se o token é válido
    token_valido = verificar_token_recuperacao(
        dados.token,
        email
    )

    if not token_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

    # Procura o cliente no banco
    consulta = select(Cliente).where(
        Cliente.email == email
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    # Cria o hash da nova senha
    cliente.senha_hash = criar_hash_senha(
        dados.nova_senha
    )

    # Salva a nova senha no MySQL
    database.commit()
    database.refresh(cliente)

    return {
        "mensagem": (
            "Senha alterada com sucesso. "
            "Você já pode realizar o login."
        )
    }