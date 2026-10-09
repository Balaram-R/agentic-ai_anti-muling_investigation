from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class InvestigatorEvidence(BaseModel):
    alert: dict[str, Any]
    account: dict[str, Any]
    transactions: list[dict[str, Any]]
    aml_profile: dict[str, Any]
    behavior: dict[str, Any]


class InvestigatorResult(BaseModel):
    alert_id: str
    account_id: str
    evidence: InvestigatorEvidence