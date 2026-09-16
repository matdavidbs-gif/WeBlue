from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_database
from ..models.cliente import Cliente
from ..schemas.login import LoginEntrada, LoginResposta
from ..services.security import verificar_senha, criar_token_acesso


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
    # Procura o cliente pelo e-mail
    consulta = select(Cliente).where(
        Cliente.email == str(dados.email)
    )

    cliente = database.scalar(consulta)

    # Verifica se o cliente existe e se a senha está correta
    if cliente is None or not verificar_senha(
        dados.senha,
        cliente.senha_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    # Verifica se a conta está bloqueada
    if cliente.status == "BLOQUEADA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está bloqueada."
        )

    # Verifica se a conta está inativa
    if cliente.status == "INATIVA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está inativa."
        )

    # Gera o JWT
    # Se "lembrar" for True, o token terá duração maior
    token = criar_token_acesso(
        cliente_id=cliente.id,
        lembrar=dados.lembrar
    )

    # Retorna o token e os dados básicos do cliente
    return {
        "mensagem": "Login realizado com sucesso.",
        "access_token": token,
        "token_type": "bearer",
        "cliente": {
            "id": cliente.id,
            "nome_completo": cliente.nome_completo,
            "email": cliente.email,
            "status": cliente.status
        }
    }