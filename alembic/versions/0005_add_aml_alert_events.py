"""add aml alert events

Revision ID: 0005_add_aml_alert_events
Revises: 0004_add_aml_alert_transactions
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_aml_alert_events"
down_revision: Union[str, Sequence[str], None] = "0004_add_aml_alert_transactions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aml_alert_events",
        sa.Column(
            "event_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "alert_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "old_status",
            sa.String(length=30),
            nullable=True,
        ),
        sa.Column(
            "new_status",
            sa.String(length=30),
            nullable=True,
        ),
        sa.Column(
            "event_time",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["aml_alerts.alert_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )

    op.create_index(
        "ix_aml_alert_events_alert_id",
        "aml_alert_events",
        ["alert_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_aml_alert_events_alert_id",
        table_name="aml_alert_events",
    )

    op.drop_table("aml_alert_events")