from app.agents.schemas import InvestigatorEvidence, InvestigatorResult
from app.agents.tool_registry import ToolRegistry
from app.models.agent_execution import AgentExecutionStatus
from app.services.agent_execution_service import AgentExecutionService


class InvestigatorAgent:
    def __init__(
        self,
        tool_registry: ToolRegistry | None = None,
        execution_service: AgentExecutionService | None = None,
    ):
        self.tools = tool_registry or ToolRegistry()
        self.execution_service = execution_service or AgentExecutionService()

    def investigate(self, db, alert_id: str, investigation_id: str | None = None) -> InvestigatorResult:
        alert = self.tools.get_alert_evidence(db, alert_id)

        if investigation_id:
            self.execution_service.record(
                db=db,
                investigation_id=investigation_id,
                agent_name="InvestigatorAgent",
                tool_name="get_alert_evidence",
                status=AgentExecutionStatus.SUCCESS,
                summary=f"Retrieved AML alert evidence for alert {alert_id}.",
            )

        account = self.tools.get_account(
            db,
            alert["account_id"],
        )

        if investigation_id:
            self.execution_service.record(
                db=db,
                investigation_id=investigation_id,
                agent_name="InvestigatorAgent",
                tool_name="get_account",
                status=AgentExecutionStatus.SUCCESS,
                summary=f"Retrieved account profile for {alert['account_id']}.",
            )

        transactions = self.tools.get_transactions(
            db,
            alert["account_id"],
            transaction_ids=alert["transaction_ids"],
        )

        if investigation_id:
            self.execution_service.record(
                db=db,
                investigation_id=investigation_id,
                agent_name="InvestigatorAgent",
                tool_name="get_transactions",
                status=AgentExecutionStatus.SUCCESS,
                summary=f"Retrieved {len(transactions)} alert-linked transactions.",
            )

        aml_profile = self.tools.get_aml_profile(
            db,
            alert["account_id"],
        )

        if investigation_id:
            self.execution_service.record(
                db=db,
                investigation_id=investigation_id,
                agent_name="InvestigatorAgent",
                tool_name="get_aml_profile",
                status=AgentExecutionStatus.SUCCESS,
                summary=f"Retrieved AML profile for {alert['account_id']}.",
            )


        behavior = self.tools.get_account_behavior(
            db,
            alert["account_id"],
        )

        if investigation_id:
            self.execution_service.record(
                db=db,
                investigation_id=investigation_id,
                agent_name="InvestigatorAgent",
                tool_name="get_account_behavior",
                status=AgentExecutionStatus.SUCCESS,
                summary=(
                    f"Retrieved behavioral analysis for "
                    f"{alert['account_id']}."
                ),
            )

        evidence = InvestigatorEvidence(
            alert=alert,
            account=account,
            transactions=transactions,
            aml_profile=aml_profile,
            behavior=behavior,
        )

        return InvestigatorResult(
            alert_id=alert["alert_id"],
            account_id=alert["account_id"],
            evidence=evidence,
        )