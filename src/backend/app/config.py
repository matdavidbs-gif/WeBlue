from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =========================
    # BANCO DE DADOS
    # =========================

    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "weblue"

    # =========================
    # JWT
    # =========================

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # =========================
    # E-MAIL DE RECUPERAÇÃO
    # =========================

    smtp_host: str | None = None
    smtp_port: int = 465
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: EmailStr | None = None
    frontend_base_url: str | None = None
    smtp_timeout_seconds: int = 10

    # =========================
    # ARQUIVO .ENV
    # =========================

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()