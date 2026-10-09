from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AMLAlertEvent(Base):
    __tablename__ = "aml_alert_events"

    event_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    alert_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("aml_alerts.alert_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    new_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )