from pydantic import BaseModel, EmailStr, Field


class LoginEntrada(BaseModel):
    email: EmailStr

    senha: str = Field(
        min_length=8,
        max_length=128
    )

    lembrar: bool = False


class ClienteAutenticado(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    status: str


class LoginResposta(BaseModel):
    mensagem: str
    access_token: str
    token_type: str
    cliente: ClienteAutenticado