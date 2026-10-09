"""add aml alerts

Revision ID: 0003_add_aml_alerts
Revises: 0002_aml_profiles
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_aml_alerts"
down_revision: Union[str, Sequence[str], None] = "0002_aml_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


aml_alert_severity = sa.Enum(
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
    name="aml_alert_severity",
    create_type=False,
)

aml_alert_status = sa.Enum(
    "OPEN",
    "UNDER_REVIEW",
    "CLOSED",
    name="aml_alert_status",
    create_type=False,
)


def upgrade() -> None:
    severity_type = sa.Enum(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="aml_alert_severity",
    )

    status_type = sa.Enum(
        "OPEN",
        "UNDER_REVIEW",
        "CLOSED",
        name="aml_alert_status",
    )

    severity_type.create(op.get_bind(), checkfirst=True)
    status_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "aml_alerts",
        sa.Column("alert_id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=32), nullable=False),
        sa.Column("rule_code", sa.String(length=50), nullable=False),
        sa.Column(
            "severity",
            aml_alert_severity,
            nullable=False,
        ),
        sa.Column(
            "status",
            aml_alert_status,
            nullable=False,
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "transaction_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "combined_amount",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.String(length=500),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.account_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("alert_id"),
    )

    op.create_index(
        "ix_aml_alerts_account_id",
        "aml_alerts",
        ["account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_aml_alerts_account_id",
        table_name="aml_alerts",
    )

    op.drop_table("aml_alerts")

    op.execute("DROP TYPE IF EXISTS aml_alert_status")
    op.execute("DROP TYPE IF EXISTS aml_alert_severity")