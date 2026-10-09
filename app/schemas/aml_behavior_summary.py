from pydantic import BaseModel


class AMLBehaviorSummary(BaseModel):
    finding_count: int
    highest_severity: str | None