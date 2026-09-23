# ============================================================
# WEBLUE - MODELO DE ADMINISTRADOR
# ============================================================
#
# Este arquivo representa a tabela "administradores"
# no banco de dados.
#
# O administrador terá autenticação separada dos clientes.
# A senha nunca será armazenada em texto puro.
# ============================================================


from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from ..database import Base


# ============================================================
# MODELO ADMINISTRADOR
# ============================================================

class Administrador(Base):

    # Nome da tabela que será criada no MySQL.
    __tablename__ = "administradores"


    # ========================================================
    # ID
    # ========================================================

    # Identificador único do administrador.
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )


    # ========================================================
    # NOME
    # ========================================================

    nome = Column(
        String(150),
        nullable=False
    )


    # ========================================================
    # E-MAIL
    # ========================================================

    # O e-mail será utilizado para realizar o login.
    #
    # unique=True impede dois administradores
    # com o mesmo e-mail.
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )


    # ========================================================
    # SENHA
    # ========================================================

    # Nunca armazenamos a senha original.
    #
    # Aqui ficará somente o hash seguro da senha.
    senha_hash = Column(
        String(255),
        nullable=False
    )


    # ========================================================
    # STATUS
    # ========================================================

    # Permite bloquear o acesso de um administrador
    # sem precisar excluir sua conta.
    ativo = Column(
        Boolean,
        nullable=False,
        default=True
    )


    # ========================================================
    # DATA DE CRIAÇÃO
    # ========================================================

    data_criacao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )


    # ========================================================
    # DATA DE ATUALIZAÇÃO
    # ========================================================

    data_atualizacao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )