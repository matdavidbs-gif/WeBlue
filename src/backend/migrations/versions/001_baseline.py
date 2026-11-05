"""Create the existing application schema when missing.

Revision ID: 001_baseline
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect


revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def _exists(table_name):
    if op.get_context().as_sql:
        return False
    return table_name in inspect(op.get_bind()).get_table_names()


def upgrade():
    if not _exists("administradores"):
        op.create_table(
            "administradores",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("nome", sa.String(length=150), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("senha_hash", sa.String(length=255), nullable=False),
            sa.Column("ativo", sa.Boolean(), nullable=False),
            sa.Column("data_criacao", sa.DateTime(), nullable=False),
            sa.Column("data_atualizacao", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_administradores_email",
            "administradores",
            ["email"],
            unique=True,
        )
        op.create_index(
            "ix_administradores_id",
            "administradores",
            ["id"],
            unique=False,
        )

    if not _exists("clientes"):
        op.create_table(
            "clientes",
            sa.Column(
                "id",
                mysql.BIGINT(unsigned=True),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column("nome_completo", sa.String(length=150), nullable=False),
            sa.Column("email", sa.String(length=254), nullable=False),
            sa.Column("cpf", sa.String(length=11), nullable=False),
            sa.Column("telefone", sa.String(length=11), nullable=False),
            sa.Column("senha_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "status",
                mysql.ENUM("ATIVA", "INATIVA", "BLOQUEADA"),
                server_default="ATIVA",
                nullable=False,
            ),
            sa.Column("aceitou_termos_em", sa.DateTime(), nullable=False),
            sa.Column(
                "criado_em",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "atualizado_em",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("cpf"),
            sa.UniqueConstraint("email"),
        )

    if not _exists("produtos"):
        op.create_table(
            "produtos",
            sa.Column(
                "id",
                mysql.BIGINT(unsigned=True),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column("nome", sa.String(length=150), nullable=False),
            sa.Column("descricao", sa.Text(), nullable=False),
            sa.Column("preco", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("estoque", sa.Integer(), nullable=False),
            sa.Column("categoria", sa.String(length=100), nullable=False),
            sa.Column("marca", sa.String(length=100), nullable=False),
            sa.Column("imagem_url", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("data_criacao", sa.DateTime(), nullable=False),
            sa.Column("data_atualizacao", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _exists("clientes_versoes_autenticacao"):
        op.create_table(
            "clientes_versoes_autenticacao",
            sa.Column(
                "cliente_id",
                mysql.BIGINT(unsigned=True),
                nullable=False,
            ),
            sa.Column("versao", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["cliente_id"],
                ["clientes.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("cliente_id"),
        )

    if not _exists("tokens_recuperacao_senha"):
        op.create_table(
            "tokens_recuperacao_senha",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column(
                "cliente_id",
                mysql.BIGINT(unsigned=True),
                nullable=False,
            ),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expira_em", sa.DateTime(), nullable=False),
            sa.Column("usado_em", sa.DateTime(), nullable=True),
            sa.Column(
                "criado_em",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["cliente_id"],
                ["clientes.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("token_hash"),
        )
        op.create_index(
            "ix_tokens_recuperacao_senha_cliente_id",
            "tokens_recuperacao_senha",
            ["cliente_id"],
            unique=False,
        )
        op.create_index(
            "ix_tokens_recuperacao_senha_expira_em",
            "tokens_recuperacao_senha",
            ["expira_em"],
            unique=False,
        )

    if not _exists("pedidos"):
        op.create_table(
            "pedidos",
            sa.Column(
                "id",
                mysql.BIGINT(unsigned=True),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "cliente_id",
                mysql.BIGINT(unsigned=True),
                nullable=False,
            ),
            sa.Column(
                "status",
                mysql.ENUM(
                    "PENDENTE",
                    "PAGO",
                    "EM_SEPARACAO",
                    "ENVIADO",
                    "ENTREGUE",
                    "CANCELADO",
                ),
                server_default="PENDENTE",
                nullable=False,
            ),
            sa.Column("valor_total", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column(
                "criado_em",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "atualizado_em",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _exists("itens_pedido"):
        op.create_table(
            "itens_pedido",
            sa.Column(
                "id",
                mysql.BIGINT(unsigned=True),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "pedido_id",
                mysql.BIGINT(unsigned=True),
                nullable=False,
            ),
            sa.Column(
                "produto_id",
                mysql.BIGINT(unsigned=True),
                nullable=False,
            ),
            sa.Column("quantidade", sa.Integer(), nullable=False),
            sa.Column("preco_unitario", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("subtotal", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
            sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    # This baseline also adopts existing databases; dropping these tables risks
    # deleting application data during a downgrade.
    pass
