"""add agent executions

Revision ID: 0ad1731d0696
Revises: 0006_add_aml_investigations
Create Date: 2026-09-30 23:10:07.072476
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0ad1731d0696"
down_revision: Union[str, Sequence[str], None] = "0006_add_aml_investigations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_executions",
        sa.Column("execution_id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "SUCCESS",
                "FAILED",
                name="agent_execution_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("summary", sa.String(length=1000), nullable=False),
        sa.ForeignKeyConstraint(
            ["investigation_id"],
            ["aml_investigations.investigation_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("execution_id"),
    )

    op.create_index(
        "ix_agent_executions_investigation_id",
        "agent_executions",
        ["investigation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_executions_investigation_id",
        table_name="agent_executions",
    )

    op.drop_table("agent_executions")

    sa.Enum(
        "SUCCESS",
        "FAILED",
        name="agent_execution_status",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )