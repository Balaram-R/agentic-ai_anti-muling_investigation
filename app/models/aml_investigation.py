import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvestigationStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class AMLInvestigation(Base):
    __tablename__ = "aml_investigations"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    alert_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("aml_alerts.alert_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[InvestigationStatus] = mapped_column(
        Enum(
            InvestigationStatus,
            name="investigation_status",
        ),
        nullable=False,
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    conclusion: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    analysis_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analysis_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    analysis_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    alert = relationship("AMLAlert")