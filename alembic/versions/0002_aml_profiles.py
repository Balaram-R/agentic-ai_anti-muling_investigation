"""add aml profiles

Revision ID: 0002_aml_profiles
Revises: 0001_initial
Create Date: 2026-09-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_aml_profiles"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


customer_risk_category = sa.Enum(
    "LOW",
    "MEDIUM",
    "HIGH",
    name="customer_risk_category",
    create_type=False,
)


def upgrade() -> None:
    # Create the PostgreSQL enum explicitly.
    enum_type = sa.Enum(
        "LOW",
        "MEDIUM",
        "HIGH",
        name="customer_risk_category",
    )
    enum_type.create(op.get_bind(), checkfirst=True)

    # Then create the AML profile table using the existing enum.
    op.create_table(
        "aml_profiles",
        sa.Column("account_id", sa.String(length=32), nullable=False),
        sa.Column(
            "risk_category",
            customer_risk_category,
            nullable=False,
        ),
        sa.Column(
            "expected_min_transaction",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "expected_max_transaction",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "expected_daily_transaction_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "expected_monthly_volume",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "baseline_window_days",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.account_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("account_id"),
    )


def downgrade() -> None:
    op.drop_table("aml_profiles")

    enum_type = sa.Enum(
        "LOW",
        "MEDIUM",
        "HIGH",
        name="customer_risk_category",
    )
    enum_type.drop(op.get_bind(), checkfirst=True)