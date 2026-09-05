from pydantic import BaseModel, EmailStr, Field, model_validator


class RecuperacaoSenhaRequest(BaseModel):
    email: EmailStr
    nova_senha: str = Field(min_length=8)
    confirmar_senha: str = Field(min_length=8)

    @model_validator(mode="after")
    def validar_senhas(self):
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem.")

        return self