from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.aml_investigation import InvestigationStatus

from app.schemas.aml_alert import AMLAlertRead
from app.schemas.account import AccountRead
from app.schemas.transaction import TransactionRead
from app.schemas.aml_profile import AMLProfileRead
from app.schemas.aml_behavior import AMLBehaviorRead


class AMLInvestigationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    investigation_id: str
    alert_id: str
    assigned_to: str | None
    status: InvestigationStatus
    opened_at: datetime
    closed_at: datetime | None
    conclusion: str | None


class AMLInvestigationCreate(BaseModel):
    assigned_to: str | None = None


class AMLInvestigationStatusUpdate(BaseModel):
    status: InvestigationStatus
    conclusion: str | None = None


class AMLFindingRead(BaseModel):
    code: str
    severity: str
    title: str
    description: str
    evidence: list[str]

class AMLCaseAssessmentRead(BaseModel):
    outcome: str
    rationale: str
    finding_codes: list[str]


class AMLRecommendationRead(BaseModel):
    action: str
    rationale: str
    requires_human_approval: bool

class AgentExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str
    investigation_id: str
    agent_name: str
    tool_name: str
    status: str
    executed_at: datetime
    summary: str

class AMLInvestigationCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    investigation: AMLInvestigationRead
    alert: AMLAlertRead
    account: AccountRead
    aml_profile: AMLProfileRead
    behavior: AMLBehaviorRead
    transactions: list[TransactionRead]
    audit_events: list[dict]
    findings: list[AMLFindingRead]
    assessment: AMLCaseAssessmentRead
    recommendation: AMLRecommendationRead
    agent_analysis: dict | None = None
    agent_executions: list[AgentExecutionRead] = []