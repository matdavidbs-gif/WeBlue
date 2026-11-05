from datetime import datetime

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class TokenRevogado(Base):
    __tablename__ = "tokens_revogados"

    jti: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    expira_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
