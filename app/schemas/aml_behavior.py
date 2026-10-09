from pydantic import BaseModel

from app.schemas.aml_behavior_finding import AMLBehaviorFinding

from app.schemas.aml_behavior_finding import AMLBehaviorFinding

from app.schemas.aml_behavior_summary import AMLBehaviorSummary

class AMLMonthlyBehavior(BaseModel):
    month: str
    transaction_count: int
    incoming: str
    outgoing: str


class AMLEvidence(BaseModel):
    code: str
    message: str
    details: dict


class AMLBehaviorRead(BaseModel):
    account_id: str
    monthly: list[AMLMonthlyBehavior]
    evidence: list[AMLEvidence]
    findings: list[AMLBehaviorFinding]
    summary: AMLBehaviorSummary