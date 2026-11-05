# ============================================================
# TESTES DO FLUXO DE VENDAS
# ============================================================
#
# Os testes abaixo validam:
#
# 1. cadastro de pedido com estoque suficiente
# 2. rejeição de venda sem estoque
# 3. atualização de saldo após confirmação
# ============================================================

from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import api_router
from app.database import get_database
from app.models.cliente import Cliente
from app.models.cliente_versao_autenticacao import ClienteVersaoAutenticacao
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.rate_limit_window import RateLimitWindow
from app.models.token_revogado import TokenRevogado
from app.services.security import criar_token_acesso


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
def sales_database_session():
    Cliente.__table__.create(bind=engine, checkfirst=True)
    ClienteVersaoAutenticacao.__table__.create(bind=engine, checkfirst=True)
    Produto.__table__.create(bind=engine, checkfirst=True)
    Pedido.__table__.create(bind=engine, checkfirst=True)
    ItemPedido.__table__.create(bind=engine, checkfirst=True)
    RateLimitWindow.__table__.create(bind=engine, checkfirst=True)
    TokenRevogado.__table__.create(bind=engine, checkfirst=True)

    session = TestingSessionLocal()
    try:
        session.query(ItemPedido).delete()
        session.query(Pedido).delete()
        session.query(RateLimitWindow).delete()
        session.query(TokenRevogado).delete()
        session.query(ClienteVersaoAutenticacao).delete()
        session.query(Cliente).delete()
        session.query(Produto).delete()
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def sales_client_app():
    app = FastAPI()
    app.include_router(api_router)

    def override_get_database():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_database] = override_get_database
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_authenticated_checkout_tracks_customer_orders(sales_database_session, sales_client_app):
    cliente = Cliente(
        id=1,
        nome_completo="Cliente Weblue",
        email="cliente@weblue.com",
        cpf="12345678901",
        telefone="11977778888",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=101,
        nome="Óleo Facial",
        descricao="Óleo leve para pele mista.",
        preco=59.90,
        estoque=4,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(cliente)
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
        json={
            "endereco": "Avenida do Sol, 150",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 101, "quantidade": 2}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pedido"]["status"] == "PAGO"
    assert payload["pedido"]["valor_total"] == "119.80"
    assert payload["pedido"]["id"] > 0

    historico = sales_client_app.get(
        "/api/pedidos/me",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
    )
    assert historico.status_code == 200
    assert historico.json()["total"] == 1

    sales_database_session.refresh(produto)
    assert produto.estoque == 2
    item_pedido = sales_database_session.query(ItemPedido).one()
    assert item_pedido.id > 0


def test_checkout_approves_sale_and_reduces_stock(sales_database_session, sales_client_app):
    cliente = Cliente(
        id=2,
        nome_completo="Maria Souza",
        email="maria@weblue.com",
        cpf="98765432100",
        telefone="11999999999",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=102,
        nome="Sérum Vitamina C",
        descricao="Sérum para brilho e luminosidade.",
        preco=49.90,
        estoque=5,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(cliente)
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
        json={
            "endereco": "Rua das Flores, 123",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 102, "quantidade": 2}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pedido"]["status"] == "PAGO"
    assert payload["pedido"]["valor_total"] == "99.80"

    sales_database_session.refresh(produto)
    assert produto.estoque == 3

    historico = sales_client_app.get(
        "/api/pedidos/me",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
    )
    assert historico.status_code == 200
    assert historico.json()["total"] == 1


def test_checkout_and_order_history_require_authenticated_customer(
    sales_database_session, sales_client_app
):
    cliente = Cliente(
        id=3,
        nome_completo="Cliente Autenticado",
        email="autenticado@weblue.com",
        cpf="11111111111",
        telefone="11911111111",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    sales_database_session.add(cliente)
    sales_database_session.commit()

    checkout = sales_client_app.post(
        "/api/pedidos/checkout",
        json={
            "endereco": "Rua das Flores, 123",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 101, "quantidade": 1}],
        },
    )
    historico = sales_client_app.get("/api/pedidos/me?email=autenticado@weblue.com")

    assert checkout.status_code == 401
    assert historico.status_code == 401


def test_checkout_identity_and_history_are_scoped_to_token(
    sales_database_session, sales_client_app
):
    cliente_autenticado = Cliente(
        id=4,
        nome_completo="Cliente Autenticado",
        email="autenticado@weblue.com",
        cpf="22222222222",
        telefone="11922222222",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    outro_cliente = Cliente(
        id=5,
        nome_completo="Outro Cliente",
        email="outro@weblue.com",
        cpf="33333333333",
        telefone="11933333333",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=104,
        nome="Protetor Solar",
        descricao="Proteção diária.",
        preco=Decimal("29.90"),
        estoque=3,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add_all([cliente_autenticado, outro_cliente, produto])
    sales_database_session.commit()

    compra = sales_client_app.post(
        "/api/pedidos/checkout",
        headers={
            "Authorization": f"Bearer {criar_token_acesso(cliente_autenticado.id)}"
        },
        json={
            "cliente_id": outro_cliente.id,
            "email": outro_cliente.email,
            "endereco": "Rua das Flores, 123",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": produto.id, "quantidade": 1}],
        },
    )

    historico_autenticado = sales_client_app.get(
        "/api/pedidos/me",
        headers={
            "Authorization": f"Bearer {criar_token_acesso(cliente_autenticado.id)}"
        },
    )
    historico_outro_cliente = sales_client_app.get(
        "/api/pedidos/me",
        headers={"Authorization": f"Bearer {criar_token_acesso(outro_cliente.id)}"},
    )

    assert compra.status_code == 200
    pedido = sales_database_session.query(Pedido).one()
    assert pedido.cliente_id == cliente_autenticado.id
    assert historico_autenticado.json()["total"] == 1
    assert historico_outro_cliente.json()["total"] == 0


def test_checkout_rejects_sale_without_stock(sales_database_session, sales_client_app):
    cliente = Cliente(
        id=6,
        nome_completo="João Silva",
        email="joao@weblue.com",
        cpf="44444444444",
        telefone="11888888888",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=103,
        nome="Creme Hidratante",
        descricao="Creme para pele seca.",
        preco=39.99,
        estoque=1,
        categoria="Corpo",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add(cliente)
    sales_database_session.add(produto)
    sales_database_session.commit()

    response = sales_client_app.post(
        "/api/pedidos/checkout",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
        json={
            "endereco": "Avenida Paulista, 99",
            "metodo_pagamento": "PIX",
            "itens": [{"produto_id": 103, "quantidade": 2}],
        },
    )

    assert response.status_code == 400
    assert "estoque" in response.json()["detail"].lower()

    sales_database_session.refresh(produto)
    assert produto.estoque == 1


def test_checkout_sums_repeated_products_before_checking_stock(
    sales_database_session, sales_client_app
):
    cliente = Cliente(
        id=7,
        nome_completo="Cliente Weblue",
        email="repetido@weblue.com",
        cpf="55555555555",
        telefone="11955555555",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=105,
        nome="Sérum",
        descricao="Sérum facial.",
        preco=Decimal("10.00"),
        estoque=3,
        categoria="Skincare",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add_all([cliente, produto])
    sales_database_session.commit()

    resposta = sales_client_app.post(
        "/api/pedidos/checkout",
        headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
        json={
            "endereco": "Rua das Flores, 123",
            "metodo_pagamento": "PIX",
            "itens": [
                {"produto_id": produto.id, "quantidade": 2},
                {"produto_id": produto.id, "quantidade": 2},
            ],
        },
    )

    assert resposta.status_code == 400
    sales_database_session.refresh(produto)
    assert produto.estoque == 3
    assert sales_database_session.query(Pedido).count() == 0


def test_checkout_rolls_back_stock_and_order_when_item_insert_fails(
    sales_database_session, sales_client_app
):
    cliente = Cliente(
        id=8,
        nome_completo="Cliente Weblue",
        email="rollback@weblue.com",
        cpf="66666666666",
        telefone="11966666666",
        senha_hash="hash-de-teste",
        status="ATIVA",
        aceitou_termos_em=datetime.now(),
    )
    produto = Produto(
        id=106,
        nome="Creme",
        descricao="Creme hidratante.",
        preco=Decimal("20.00"),
        estoque=4,
        categoria="Corpo",
        marca="Weblue",
        imagem_url=None,
        status="ATIVO",
    )
    sales_database_session.add_all([cliente, produto])
    sales_database_session.commit()

    def falhar_antes_de_inserir(mapper, connection, item):
        raise RuntimeError("Falha simulada ao gravar item.")

    event.listen(ItemPedido, "before_insert", falhar_antes_de_inserir)
    try:
        resposta = sales_client_app.post(
            "/api/pedidos/checkout",
            headers={"Authorization": f"Bearer {criar_token_acesso(cliente.id)}"},
            json={
                "endereco": "Rua das Flores, 123",
                "metodo_pagamento": "PIX",
                "itens": [{"produto_id": produto.id, "quantidade": 2}],
            },
        )
    finally:
        event.remove(ItemPedido, "before_insert", falhar_antes_de_inserir)

    assert resposta.status_code == 500
    sales_database_session.refresh(produto)
    assert produto.estoque == 4
    assert sales_database_session.query(Pedido).count() == 0
    assert sales_database_session.query(ItemPedido).count() == 0
