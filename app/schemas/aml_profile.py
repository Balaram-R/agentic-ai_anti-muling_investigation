from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.aml_profile import CustomerRiskCategory


class AMLProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: str
    risk_category: CustomerRiskCategory
    expected_min_transaction: Decimal
    expected_max_transaction: Decimal
    expected_daily_transaction_count: int
    expected_monthly_volume: Decimal
    baseline_window_days: int
