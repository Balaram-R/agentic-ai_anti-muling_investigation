import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AMLAlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AMLAlertStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLOSED = "CLOSED"


class AMLAlert(Base):
    __tablename__ = "aml_alerts"

    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)

    account_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("accounts.account_id"),
        nullable=False,
        index=True,
    )

    rule_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    severity: Mapped[AMLAlertSeverity] = mapped_column(
        Enum(AMLAlertSeverity, name="aml_alert_severity"),
        nullable=False,
    )

    status: Mapped[AMLAlertStatus] = mapped_column(
        Enum(AMLAlertStatus, name="aml_alert_status"),
        nullable=False,
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    transaction_count: Mapped[int] = mapped_column(
        nullable=False,
    )

    combined_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    account = relationship("Account")