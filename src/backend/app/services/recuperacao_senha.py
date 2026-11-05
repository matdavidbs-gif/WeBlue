import hashlib
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import quote, urljoin, urlsplit

from ..config import settings


class EmailRecuperacaoNaoConfigurado(Exception):
    pass


def criar_token_recuperacao() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return token, token_hash


def hash_token_recuperacao(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def validar_configuracao_email() -> None:
    configuracao_obrigatoria = (
        settings.smtp_host,
        settings.smtp_from_email,
        settings.frontend_base_url,
    )
    if not all(valor and valor.strip() for valor in configuracao_obrigatoria):
        raise EmailRecuperacaoNaoConfigurado

    if bool(settings.smtp_username) != bool(settings.smtp_password):
        raise EmailRecuperacaoNaoConfigurado
    if not 1 <= settings.smtp_port <= 65535 or settings.smtp_timeout_seconds <= 0:
        raise EmailRecuperacaoNaoConfigurado

    try:
        url = urlsplit(settings.frontend_base_url)
    except ValueError as erro:
        raise EmailRecuperacaoNaoConfigurado from erro
    host_local = url.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        url.scheme != "https" and not (url.scheme == "http" and host_local)
    ) or not url.hostname or url.path not in ("", "/") or url.query or url.fragment:
        raise EmailRecuperacaoNaoConfigurado


def enviar_email_recuperacao(destinatario: str, token: str) -> None:
    validar_configuracao_email()

    url_base = settings.frontend_base_url.rstrip("/") + "/"
    link = (
        urljoin(url_base, "recuperar-senha")
        + "#token="
        + quote(token, safe="")
    )

    mensagem = EmailMessage()
    mensagem["Subject"] = "Recuperação de senha Weblue"
    mensagem["From"] = settings.smtp_from_email
    mensagem["To"] = destinatario
    mensagem.set_content(
        "Recebemos uma solicitação para redefinir a senha da sua conta Weblue.\n\n"
        f"Use este link em até 15 minutos: {link}\n\n"
        "Se você não solicitou a recuperação, ignore esta mensagem."
    )

    contexto_ssl = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        settings.smtp_host,
        settings.smtp_port,
        timeout=settings.smtp_timeout_seconds,
        context=contexto_ssl,
    ) as servidor:
        if settings.smtp_username:
            servidor.login(settings.smtp_username, settings.smtp_password)
        servidor.send_message(mensagem)
