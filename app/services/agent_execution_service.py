from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent_execution import AgentExecutionStatus
from app.repositories.agent_executions import AgentExecutionRepository


class AgentExecutionService:
    def __init__(
        self,
        repository: AgentExecutionRepository | None = None,
    ):
        self.repository = repository or AgentExecutionRepository()

    def record(
        self,
        db: Session,
        investigation_id: str,
        agent_name: str,
        tool_name: str,
        status: AgentExecutionStatus,
        summary: str,
        executed_at: datetime | None = None,
    ):
        return self.repository.create(
            db=db,
            investigation_id=investigation_id,
            agent_name=agent_name,
            tool_name=tool_name,
            status=status,
            summary=summary,
            executed_at=executed_at,
        )

    def list_for_investigation(
        self,
        db: Session,
        investigation_id: str,
    ):
        return self.repository.list_for_investigation(
            db,
            investigation_id,
        )