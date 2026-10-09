"""add aml alert transactions

Revision ID: 0004_add_aml_alert_transactions
Revises: 0003_add_aml_alerts
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_add_aml_alert_transactions"
down_revision: Union[str, Sequence[str], None] = "0003_add_aml_alerts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aml_alert_transactions",
        sa.Column(
            "alert_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "transaction_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["aml_alerts.alert_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.transaction_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "alert_id",
            "transaction_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("aml_alert_transactions")