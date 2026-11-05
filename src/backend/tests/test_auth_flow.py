import hashlib
import smtplib
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import api_router
from app.database import get_database
from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.cliente_versao_autenticacao import ClienteVersaoAutenticacao
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.rate_limit_window import RateLimitWindow
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.token_revogado import TokenRevogado
from app.config import settings
from app.routers import recuperacao_senha as recovery_router
from app.services.admin_security import criar_hash_senha_admin
from app.services.security import (
    criar_hash_senha,
    criar_refresh_token_cliente,
    criar_token_acesso,
    revogar_token,
    verificar_senha,
    verificar_token_acesso,
)
from app.services import recuperacao_senha as recovery_service


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def database_session():
    Cliente.__table__.create(bind=engine, checkfirst=True)
    ClienteVersaoAutenticacao.__table__.create(bind=engine, checkfirst=True)
    Administrador.__table__.create(bind=engine, checkfirst=True)
    Produto.__table__.create(bind=engine, checkfirst=True)
    TokenRecuperacaoSenha.__table__.create(bind=engine, checkfirst=True)
    RateLimitWindow.__table__.create(bind=engine, checkfirst=True)
    TokenRevogado.__table__.create(bind=engine, checkfirst=True)

    session = TestingSessionLocal()
    try:
        session.query(TokenRecuperacaoSenha).delete()
        session.query(RateLimitWindow).delete()
        session.query(TokenRevogado).delete()
        session.query(ClienteVersaoAutenticacao).delete()
        session.query(Cliente).delete()
        session.query(Administrador).delete()
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def client_app():
    app = FastAPI()
    app.include_router(api_router)

    def override_get_database():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_cliente_login_profile_flow(database_session, client_app):
    senha = "SenhaForte123"
    cliente = Cliente(
        id=1,
        nome_completo="Ana Souza",
        email="ana@weblue.com",
        cpf="12345678901",
        telefone="11999999999",
        senha_hash=criar_hash_senha(senha),
        status="ATIVA",
        aceitou_termos_em=datetime.now(UTC).replace(tzinfo=None),
    )
    database_session.add(cliente)
    database_session.commit()
    database_session.refresh(cliente)

    response = client_app.post(
        "/api/auth/login",
        json={"email": cliente.email, "senha": senha, "lembrar": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cliente"]["email"] == cliente.email
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"

    token = payload["access_token"]
    perfil_response = client_app.get(
        "/api/perfil",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert perfil_response.status_code == 200
    perfil = perfil_response.json()
    assert perfil["email"] == cliente.email
    assert perfil["status"] == "ATIVA"

    update_response = client_app.put(
        "/api/perfil",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome_completo": "Ana Pereira",
            "email": "ana.nova@weblue.com",
            "telefone": "11888888888",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["cliente"]["email"] == "ana.nova@weblue.com"
    assert updated["cliente"]["nome_completo"] == "Ana Pereira"


def test_admin_login_returns_public_data(database_session, client_app):
    senha = "SenhaAdmin123"
    administrador = Administrador(
        id=1,
        nome="Admin Central",
        email="admin@weblue.com",
        senha_hash=criar_hash_senha_admin(senha),
        ativo=True,
    )
    database_session.add(administrador)
    database_session.commit()
    database_session.refresh(administrador)

    response = client_app.post(
        "/api/admin/auth/login",
        json={"email": administrador.email, "senha": senha},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["administrador"]["email"] == administrador.email
    assert payload["administrador"]["nome"] == administrador.nome
    assert "senha_hash" not in payload["administrador"]
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"


def test_admin_products_require_valid_token(database_session, client_app):
    senha = "SenhaAdmin123"
    administrador = Administrador(
        id=1,
        nome="Admin Central",
        email="admin@weblue.com",
        senha_hash=criar_hash_senha_admin(senha),
        ativo=True,
    )
    database_session.add(administrador)
    database_session.commit()
    database_session.refresh(administrador)

    resposta_sem_token = client_app.get("/api/produtos")
    assert resposta_sem_token.status_code == 401

    resposta_login = client_app.post(
        "/api/admin/auth/login",
        json={"email": administrador.email, "senha": senha},
    )
    assert resposta_login.status_code == 200
    token = resposta_login.json()["access_token"]

    resposta_com_token = client_app.get(
        "/api/produtos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta_com_token.status_code == 200
    assert "produtos" in resposta_com_token.json()


def test_login_rate_limit_is_shared_between_database_sessions(
    database_session, client_app
):
    for _ in range(5):
        response = client_app.post(
            "/api/auth/login",
            json={"email": "tentativas@weblue.com", "senha": "SenhaIncorreta123"},
        )
        assert response.status_code == 401

    limited_response = client_app.post(
        "/api/auth/login",
        json={"email": "tentativas@weblue.com", "senha": "SenhaIncorreta123"},
    )

    assert limited_response.status_code == 429

    outra_sessao = TestingSessionLocal()
    try:
        assert outra_sessao.query(RateLimitWindow).count() == 1
    finally:
        outra_sessao.close()


def test_revoked_access_token_is_rejected_from_another_session(database_session):
    token = criar_token_acesso(cliente_id=999)
    revogar_token(token, database_session)

    outra_sessao = TestingSessionLocal()
    try:
        assert verificar_token_acesso(token, outra_sessao) is None
        assert outra_sessao.query(TokenRevogado).count() == 1
    finally:
        outra_sessao.close()


def _criar_cliente_recuperacao(
    database_session, email="ana.recuperacao@weblue.com"
):
    cliente = Cliente(
        id=42,
        nome_completo="Ana Souza",
        email=email,
        cpf="12345678901",
        telefone="11999999999",
        senha_hash=criar_hash_senha("SenhaAntiga123!"),
        status="ATIVA",
        aceitou_termos_em=datetime.now(UTC).replace(tzinfo=None),
    )
    database_session.add(cliente)
    database_session.commit()
    return cliente


def _configurar_email_recuperacao(monkeypatch):
    monkeypatch.setattr(settings, "smtp_host", "smtp.exemplo.com")
    monkeypatch.setattr(settings, "smtp_port", 465)
    monkeypatch.setattr(settings, "smtp_username", "weblue")
    monkeypatch.setattr(settings, "smtp_password", "senha-de-teste")
    monkeypatch.setattr(settings, "smtp_from_email", "no-reply@weblue.com")
    monkeypatch.setattr(settings, "frontend_base_url", "https://weblue.com")


def test_password_recovery_sends_hashed_single_use_token(
    database_session, client_app, monkeypatch
):
    cliente = _criar_cliente_recuperacao(
        database_session, "single-use@weblue.com"
    )
    token_acesso_antigo = criar_token_acesso(cliente.id)
    token_refresh_antigo, _ = criar_refresh_token_cliente(cliente.id)
    _configurar_email_recuperacao(monkeypatch)
    emails = []
    monkeypatch.setattr(
        recovery_router,
        "enviar_email_recuperacao",
        lambda email, token: emails.append((email, token)),
    )

    solicitacao = client_app.post(
        "/api/auth/solicitar-recuperacao",
        json={"email": cliente.email},
    )

    assert solicitacao.status_code == 200
    assert solicitacao.json()["mensagem"]
    assert len(emails) == 1
    assert emails[0][0] == cliente.email

    token = emails[0][1]
    registro = database_session.query(TokenRecuperacaoSenha).one()
    assert registro.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert token not in registro.token_hash

    redefinicao = client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": token,
            "nova_senha": "SenhaNova123!",
            "confirmar_senha": "SenhaNova123!",
        },
    )

    assert redefinicao.status_code == 200
    database_session.refresh(cliente)
    database_session.refresh(registro)
    assert verificar_senha("SenhaNova123!", cliente.senha_hash)
    assert not verificar_senha("SenhaAntiga123!", cliente.senha_hash)
    assert registro.usado_em is not None
    assert database_session.get(
        ClienteVersaoAutenticacao, cliente.id
    ).versao == 1

    perfil_com_token_antigo = client_app.get(
        "/api/perfil",
        headers={"Authorization": f"Bearer {token_acesso_antigo}"},
    )
    refresh_antigo = client_app.post(
        "/api/auth/refresh",
        json={"refresh_token": token_refresh_antigo},
    )
    assert perfil_com_token_antigo.status_code == 401
    assert refresh_antigo.status_code == 401

    login_nova_senha = client_app.post(
        "/api/auth/login",
        json={"email": cliente.email, "senha": "SenhaNova123!"},
    )
    assert login_nova_senha.status_code == 200
    perfil_novo_token = client_app.get(
        "/api/perfil",
        headers={
            "Authorization": (
                f"Bearer {login_nova_senha.json()['access_token']}"
            )
        },
    )
    assert perfil_novo_token.status_code == 200

    token_reutilizado = client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": token,
            "nova_senha": "OutraSenha123!",
            "confirmar_senha": "OutraSenha123!",
        },
    )
    assert token_reutilizado.status_code == 401


def test_password_recovery_does_not_disclose_unknown_email(
    database_session, client_app, monkeypatch
):
    _configurar_email_recuperacao(monkeypatch)
    emails = []
    monkeypatch.setattr(
        recovery_router,
        "enviar_email_recuperacao",
        lambda email, token: emails.append((email, token)),
    )
    cliente = _criar_cliente_recuperacao(
        database_session, "unknown-email@weblue.com"
    )

    email_cadastrado = client_app.post(
        "/api/auth/solicitar-recuperacao",
        json={"email": cliente.email},
    )
    email_desconhecido = client_app.post(
        "/api/auth/solicitar-recuperacao",
        json={"email": "nao.existe@weblue.com"},
    )

    assert email_cadastrado.status_code == email_desconhecido.status_code == 200
    assert email_cadastrado.json() == email_desconhecido.json()
    assert len(emails) == 1


def test_password_recovery_invalidates_previous_token(
    database_session, client_app, monkeypatch
):
    cliente = _criar_cliente_recuperacao(
        database_session, "previous-token@weblue.com"
    )
    _configurar_email_recuperacao(monkeypatch)
    tokens = []
    monkeypatch.setattr(
        recovery_router,
        "enviar_email_recuperacao",
        lambda email, token: tokens.append(token),
    )

    for _ in range(2):
        response = client_app.post(
            "/api/auth/solicitar-recuperacao",
            json={"email": cliente.email},
        )
        assert response.status_code == 200

    assert len(tokens) == 2
    assert client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": tokens[0],
            "nova_senha": "SenhaNova123!",
            "confirmar_senha": "SenhaNova123!",
        },
    ).status_code == 401


def test_password_recovery_rejects_weak_password(
    database_session, client_app
):
    resposta = client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": "x" * 43,
            "nova_senha": "senha-fraca",
            "confirmar_senha": "senha-fraca",
        },
    )

    assert resposta.status_code == 422


def test_password_recovery_rejects_mismatched_passwords(
    database_session, client_app
):
    resposta = client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": "x" * 43,
            "nova_senha": "SenhaNova123!",
            "confirmar_senha": "SenhaDiferente123!",
        },
    )

    assert resposta.status_code == 422


def test_password_recovery_requires_email_configuration(
    database_session, client_app, monkeypatch
):
    monkeypatch.setattr(settings, "smtp_host", None)
    monkeypatch.setattr(settings, "smtp_from_email", None)
    monkeypatch.setattr(settings, "frontend_base_url", None)

    respostas = [
        client_app.post(
            "/api/auth/solicitar-recuperacao",
            json={"email": "cadastrado@weblue.com"},
        ),
        client_app.post(
            "/api/auth/solicitar-recuperacao",
            json={"email": "inexistente@weblue.com"},
        ),
    ]

    assert [resposta.status_code for resposta in respostas] == [503, 503]
    assert respostas[0].json() == respostas[1].json()
    assert database_session.query(TokenRecuperacaoSenha).count() == 0


def test_password_recovery_reports_email_delivery_failure(
    database_session, client_app, monkeypatch
):
    cliente = _criar_cliente_recuperacao(
        database_session, "delivery-failure@weblue.com"
    )
    _configurar_email_recuperacao(monkeypatch)

    def falhar_envio(email, token):
        raise smtplib.SMTPException("SMTP indisponível")

    monkeypatch.setattr(
        recovery_router,
        "enviar_email_recuperacao",
        falhar_envio,
    )

    resposta = client_app.post(
        "/api/auth/solicitar-recuperacao",
        json={"email": cliente.email},
    )

    assert resposta.status_code == 503
    registro = database_session.query(TokenRecuperacaoSenha).one()
    assert registro.usado_em is not None


def test_password_recovery_rejects_expired_token(
    database_session, client_app
):
    cliente = _criar_cliente_recuperacao(
        database_session, "expired-token@weblue.com"
    )
    token = "expired-reset-token-" + ("x" * 25)
    registro = TokenRecuperacaoSenha(
        cliente_id=cliente.id,
        token_hash=recovery_service.hash_token_recuperacao(token),
        expira_em=datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1),
    )
    database_session.add(registro)
    database_session.commit()

    resposta = client_app.post(
        "/api/auth/redefinir-senha",
        json={
            "token": token,
            "nova_senha": "SenhaNova123!",
            "confirmar_senha": "SenhaNova123!",
        },
    )

    assert resposta.status_code == 401
    database_session.refresh(cliente)
    assert verificar_senha("SenhaAntiga123!", cliente.senha_hash)


def test_password_recovery_email_contains_one_time_link(monkeypatch):
    _configurar_email_recuperacao(monkeypatch)
    mensagens = []

    class SmtpFalso:
        def __enter__(self):
            return self

        def __exit__(self, tipo, valor, traceback):
            return False

        def login(self, usuario, senha):
            assert usuario == "weblue"
            assert senha == "senha-de-teste"

        def send_message(self, mensagem):
            mensagens.append(mensagem)

    monkeypatch.setattr(
        recovery_service.smtplib,
        "SMTP_SSL",
        lambda *args, **kwargs: SmtpFalso(),
    )

    recovery_service.enviar_email_recuperacao(
        "cliente@weblue.com",
        "token-secreto-de-teste",
    )

    assert len(mensagens) == 1
    assert mensagens[0]["To"] == "cliente@weblue.com"
    assert "https://weblue.com/recuperar-senha#token=token-secreto-de-teste" in (
        mensagens[0].get_content()
    )
