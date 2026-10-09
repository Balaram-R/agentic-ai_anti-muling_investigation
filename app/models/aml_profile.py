import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CustomerRiskCategory(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AMLProfile(Base):
    """Synthetic AML customer/account baseline used by transaction monitoring."""

    __tablename__ = "aml_profiles"

    account_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("accounts.account_id", ondelete="CASCADE"), primary_key=True
    )
    risk_category: Mapped[CustomerRiskCategory] = mapped_column(
        Enum(CustomerRiskCategory, name="customer_risk_category"), nullable=False
    )
    expected_min_transaction: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    expected_max_transaction: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    expected_daily_transaction_count: Mapped[int] = mapped_column(nullable=False)
    expected_monthly_volume: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    baseline_window_days: Mapped[int] = mapped_column(nullable=False, default=90)

    account = relationship("Account", back_populates="aml_profile")
