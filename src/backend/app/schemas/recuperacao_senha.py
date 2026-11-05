import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ==========================================
# SOLICITAR RECUPERAÇÃO
# ==========================================

class SolicitarRecuperacaoRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return str(valor).strip().lower()


# ==========================================
# REDEFINIR SENHA
# ==========================================

class RedefinirSenhaRequest(BaseModel):
    token: str = Field(
        min_length=32,
        max_length=128,
    )

    nova_senha: str = Field(
        min_length=8,
        max_length=128,
    )

    confirmar_senha: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, valor: str) -> str:
        if not all(
            (
                re.search(r"[A-Z]", valor),
                re.search(r"[a-z]", valor),
                re.search(r"\d", valor),
                re.search(r"[^A-Za-z0-9]", valor),
            )
        ):
            raise ValueError(
                "A senha deve possuir letra maiúscula, minúscula, número e símbolo."
            )
        return valor

    @model_validator(mode="after")
    def validar_senhas(self) -> "RedefinirSenhaRequest":
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem.")
        return self