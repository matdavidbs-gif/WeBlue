from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class RateLimitWindow(Base):
    __tablename__ = "rate_limit_windows"

    chave: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    tentativas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    iniciada_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
