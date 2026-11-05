"""Persist rate limits and revoked tokens.

Revision ID: 002_security_state
Revises: 001_baseline
"""
from alembic import op
import sqlalchemy as sa


revision = "002_security_state"
down_revision = "001_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rate_limit_windows",
        sa.Column("chave", sa.String(length=64), nullable=False),
        sa.Column("tentativas", sa.Integer(), nullable=False),
        sa.Column("iniciada_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("chave"),
    )
    op.create_index(
        "ix_rate_limit_windows_iniciada_em",
        "rate_limit_windows",
        ["iniciada_em"],
        unique=False,
    )

    op.create_table(
        "tokens_revogados",
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index(
        "ix_tokens_revogados_expira_em",
        "tokens_revogados",
        ["expira_em"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_tokens_revogados_expira_em",
        table_name="tokens_revogados",
    )
    op.drop_table("tokens_revogados")
    op.drop_index(
        "ix_rate_limit_windows_iniciada_em",
        table_name="rate_limit_windows",
    )
    op.drop_table("rate_limit_windows")
