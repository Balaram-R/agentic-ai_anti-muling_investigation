import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AgentExecutionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "aml_investigations.investigation_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    agent_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[AgentExecutionStatus] = mapped_column(
        Enum(
            AgentExecutionStatus,
            name="agent_execution_status",
        ),
        nullable=False,
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )