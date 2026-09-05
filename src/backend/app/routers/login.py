from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..schemas.login import LoginEntrada, LoginResposta
from ..services.security import verificar_senha


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post(
    "/login",
    response_model=LoginResposta,
    status_code=status.HTTP_200_OK,
    summary="Realizar login do cliente"
)
def realizar_login(
    dados: LoginEntrada,
    database: Session = Depends(get_database)
):
    consulta = select(Cliente).where(
        Cliente.email == str(dados.email)
    )

    cliente = database.scalar(consulta)

    if cliente is None or not verificar_senha(
        dados.senha,
        cliente.senha_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    if cliente.status == "BLOQUEADA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está bloqueada."
        )

    if cliente.status == "INATIVA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está inativa."
        )

    return {
        "mensagem": "Login realizado com sucesso.",
        "cliente": {
            "id": cliente.id,
            "nome_completo": cliente.nome_completo,
            "email": cliente.email,
            "status": cliente.status
        }
    }