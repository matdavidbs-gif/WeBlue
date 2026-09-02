import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def cpf_e_valido(cpf: str) -> bool:
    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[indice]) * (10 - indice)
        for indice in range(9)
    )

    primeiro_digito = (soma * 10) % 11

    if primeiro_digito == 10:
        primeiro_digito = 0

    if primeiro_digito != int(cpf[9]):
        return False

    soma = sum(
        int(cpf[indice]) * (11 - indice)
        for indice in range(10)
    )

    segundo_digito = (soma * 10) % 11

    if segundo_digito == 10:
        segundo_digito = 0

    return segundo_digito == int(cpf[10])


class ClienteCriacao(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=150)
    email: EmailStr
    cpf: str
    telefone: str
    senha: str = Field(min_length=8, max_length=128)
    confirmar_senha: str = Field(min_length=8, max_length=128)
    aceitou_termos: bool

    @field_validator("nome_completo")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        nome = " ".join(valor.strip().split())

        if len(nome.split()) < 2:
            raise ValueError("Informe o nome completo.")

        return nome

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return str(valor).strip().lower()

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, valor: str) -> str:
        cpf = re.sub(r"\D", "", valor)

        if not cpf_e_valido(cpf):
            raise ValueError("Informe um CPF válido.")

        return cpf

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, valor: str) -> str:
        telefone = re.sub(r"\D", "", valor)

        if len(telefone) not in (10, 11):
            raise ValueError("Informe um telefone válido.")

        return telefone

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        possui_maiuscula = re.search(r"[A-Z]", valor)
        possui_minuscula = re.search(r"[a-z]", valor)
        possui_numero = re.search(r"\d", valor)
        possui_simbolo = re.search(r"[^A-Za-z0-9]", valor)

        if not all([
            possui_maiuscula,
            possui_minuscula,
            possui_numero,
            possui_simbolo,
        ]):
            raise ValueError(
                "A senha deve possuir letra maiúscula, "
                "minúscula, número e símbolo."
            )

        return valor

    @field_validator("aceitou_termos")
    @classmethod
    def validar_termos(cls, valor: bool) -> bool:
        if not valor:
            raise ValueError(
                "É necessário aceitar os termos e a política de privacidade."
            )

        return valor

    @model_validator(mode="after")
    def validar_confirmacao_senha(self):
        if self.senha != self.confirmar_senha:
            raise ValueError("As senhas informadas não coincidem.")

        return self


class ClienteResposta(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    telefone: str
    status: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)