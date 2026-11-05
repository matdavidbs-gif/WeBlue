from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ClienteVersaoAutenticacao(Base):
    __tablename__ = "clientes_versoes_autenticacao"

    cliente_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("clientes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    versao: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
