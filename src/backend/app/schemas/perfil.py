from pydantic import BaseModel, EmailStr, Field


class AtualizarPerfilRequest(BaseModel):
    nome_completo: str = Field(
        min_length=3,
        max_length=150
    )

    email: EmailStr

    telefone: str = Field(
        min_length=10,
        max_length=20
    )