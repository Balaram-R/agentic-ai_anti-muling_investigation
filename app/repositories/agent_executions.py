from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.agent_execution import (
    AgentExecution,
    AgentExecutionStatus,
)


class AgentExecutionRepository:
    def create(
        self,
        db: Session,
        investigation_id: str,
        agent_name: str,
        tool_name: str,
        status: AgentExecutionStatus,
        summary: str,
        executed_at: datetime | None = None,
    ) -> AgentExecution:
        execution = AgentExecution(
            execution_id=str(uuid4()),
            investigation_id=investigation_id,
            agent_name=agent_name,
            tool_name=tool_name,
            status=status,
            executed_at=executed_at or datetime.now().astimezone(),
            summary=summary,
        )

        db.add(execution)
        db.flush()

        return execution

    def list_for_investigation(
        self,
        db: Session,
        investigation_id: str,
    ) -> list[AgentExecution]:
        return list(
            db.query(AgentExecution)
            .filter(
                AgentExecution.investigation_id == investigation_id
            )
            .order_by(AgentExecution.executed_at.asc())
            .all()
        )