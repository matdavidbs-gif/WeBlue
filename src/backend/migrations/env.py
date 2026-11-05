from alembic import context

from app.database import Base, engine
from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.cliente_versao_autenticacao import ClienteVersaoAutenticacao
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.models.rate_limit_window import RateLimitWindow
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.token_revogado import TokenRevogado


target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
