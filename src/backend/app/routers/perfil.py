from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..services.security import verificar_token_acesso


router = APIRouter(
    prefix="/perfil",
    tags=["Perfil"]
)


seguranca = HTTPBearer()


@router.get(
    "",
    summary="Consultar perfil do cliente"
)
def consultar_perfil(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca),
    database: Session = Depends(get_database)
):
    token = credenciais.credentials

    cliente_id = verificar_token_acesso(token)

    if cliente_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

    consulta = select(Cliente).where(
        Cliente.id == cliente_id
    )

    cliente = database.scalar(consulta)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )

    if cliente.status != "ATIVA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta sem permissão de acesso."
        )

    return {
        "id": cliente.id,
        "nome_completo": cliente.nome_completo,
        "email": cliente.email,
        "cpf": cliente.cpf,
        "telefone": cliente.telefone,
        "status": cliente.status
    }