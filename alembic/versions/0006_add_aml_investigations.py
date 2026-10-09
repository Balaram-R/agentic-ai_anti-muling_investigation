"""add aml investigations

Revision ID: 0006_add_aml_investigations
Revises: 0005_add_aml_alert_events
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_add_aml_investigations"
down_revision: Union[str, None] = "0005_add_aml_alert_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    investigation_status = sa.Enum(
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED",
        name="investigation_status",
    )

    investigation_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "aml_investigations",
        sa.Column(
            "investigation_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "alert_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "assigned_to",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "OPEN",
                "IN_PROGRESS",
                "COMPLETED",
                name="investigation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "conclusion",
            sa.String(length=2000),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["aml_alerts.alert_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("investigation_id"),
        sa.UniqueConstraint("alert_id"),
    )

    op.create_index(
        "ix_aml_investigations_alert_id",
        "aml_investigations",
        ["alert_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_aml_investigations_alert_id",
        table_name="aml_investigations",
    )

    op.drop_table("aml_investigations")

    investigation_status = sa.Enum(
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED",
        name="investigation_status",
    )

    investigation_status.drop(
        op.get_bind(),
        checkfirst=True,
    )