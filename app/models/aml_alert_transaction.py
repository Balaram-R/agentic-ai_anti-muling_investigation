from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AMLAlertTransaction(Base):
    __tablename__ = "aml_alert_transactions"

    alert_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("aml_alerts.alert_id", ondelete="CASCADE"),
        primary_key=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
        primary_key=True,
    )