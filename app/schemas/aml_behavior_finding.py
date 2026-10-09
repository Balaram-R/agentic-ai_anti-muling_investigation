from pydantic import BaseModel


class AMLBehaviorFinding(BaseModel):
    code: str
    severity: str
    title: str
    description: str
    evidence: dict