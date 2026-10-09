from pydantic import BaseModel, Field


class AMLFinding(BaseModel):
    code: str
    severity: str
    description: str
    evidence: list[str] = Field(default_factory=list)


class AMLAnalysis(BaseModel):
    alert_id: str
    account_id: str
    customer_name: str
    findings: list[AMLFinding] = Field(default_factory=list)
    outcome: str