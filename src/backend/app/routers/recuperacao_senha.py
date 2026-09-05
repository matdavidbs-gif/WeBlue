from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..schemas.recuperacao_senha import RecuperacaoSenhaRequest
from ..services.security import criar_hash_senha


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post(
    "/recuperar-senha",
    status_code=status.HTTP_200_OK,
    summary="Recuperar senha do cliente"
)
def recuperar_senha(
    dados: RecuperacaoSenhaRequest,
    database: Session = Depends(get_database)
):
    consulta = select(Cliente).where(
        Cliente.email == str(dados.email)
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    cliente.senha_hash = criar_hash_senha(dados.nova_senha)

    database.commit()
    database.refresh(cliente)

    return {
        "mensagem": "Senha alterada com sucesso."
    }