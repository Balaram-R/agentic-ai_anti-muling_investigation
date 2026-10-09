from app.agents.tools.account_tools import AccountTools
from app.agents.tools.transaction_tools import TransactionTools
from app.agents.tools.aml_profile_tools import AMLProfileTools
from app.agents.tools.alert_tools import AlertTools

from app.repositories.accounts import AccountRepository
from app.repositories.transactions import TransactionRepository
from app.services.aml_behavior_service import AMLBehaviorService


class ToolRegistry:

    def __init__(self):
        self.account_tools = AccountTools()
        self.transaction_tools = TransactionTools()
        self.aml_profile_tools = AMLProfileTools()
        self.alert_tools = AlertTools()

        self.aml_behavior_service = AMLBehaviorService(
            AccountRepository(),
            TransactionRepository(),
        )

    def get_account(self, db, account_id: str):
        return self.account_tools.get_account(
            db,
            account_id,
        )

    def get_transactions(
        self,
        db,
        account_id: str,
        limit: int = 50,
        transaction_ids: list[str] | None = None,
    ):
        return self.transaction_tools.get_transactions(
            db,
            account_id,
            limit,
            transaction_ids,
        )

    def get_aml_profile(self, db, account_id: str):
        return self.aml_profile_tools.get_aml_profile(
            db,
            account_id,
        )

    def get_alert_evidence(self, db, alert_id: str):
        return self.alert_tools.get_alert_evidence(
            db,
            alert_id,
        )

    def get_account_behavior(self, db, account_id: str):
        return self.aml_behavior_service.get_behavior(
            db,
            account_id,
        )