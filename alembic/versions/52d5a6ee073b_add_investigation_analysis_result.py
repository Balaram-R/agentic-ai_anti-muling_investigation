"""add investigation analysis result

Revision ID: 52d5a6ee073b
Revises: 0ad1731d0696
Create Date: 2026-10-01 11:30:14.245785
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '52d5a6ee073b'
down_revision: Union[str, Sequence[str], None] = '0ad1731d0696'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "aml_investigations",
        sa.Column("analysis_result", sa.JSON(), nullable=True),
    )
    op.add_column(
        "aml_investigations",
        sa.Column(
            "analysis_completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "aml_investigations",
        "analysis_completed_at",
    )
    op.drop_column(
        "aml_investigations",
        "analysis_result",
    )