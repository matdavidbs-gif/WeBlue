from pydantic import BaseModel, EmailStr, Field, model_validator


# ==========================================
# SOLICITAR RECUPERAÇÃO
# ==========================================

class SolicitarRecuperacaoRequest(BaseModel):
    email: EmailStr


# ==========================================
# REDEFINIR SENHA
# ==========================================

class RedefinirSenhaRequest(BaseModel):

    email: EmailStr

    token: str = Field(
        min_length=6,
        max_length=2000
    )

    nova_senha: str = Field(
        min_length=8,
        max_length=128
    )

    confirmar_senha: str = Field(
        min_length=8,
        max_length=128
    )


    @model_validator(mode="after")
    def validar_senhas(self):

        if self.nova_senha != self.confirmar_senha:

            raise ValueError(
                "As senhas não coincidem."
            )

        return self