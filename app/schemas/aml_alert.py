from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.aml_alert import AMLAlertSeverity, AMLAlertStatus


class AMLAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    account_id: str
    rule_code: str
    severity: AMLAlertSeverity
    status: AMLAlertStatus
    triggered_at: datetime
    transaction_count: int
    combined_amount: Decimal
    reason: str


class AMLAlertDetailRead(AMLAlertRead):
    transaction_ids: list[str]

class AMLAlertStatusUpdate(BaseModel):
    status: AMLAlertStatus