from decimal import Decimal

from app.agents.investigator import InvestigatorAgent
from app.agents.schemas import InvestigatorResult


class FakeToolRegistry:

    def get_alert_evidence(self, db, alert_id):
        return {
            "alert_id": "ALERT-001",
            "account_id": "AI-ACC-1842",
            "rule_code": "STRUCTURING",
            "severity": "HIGH",
            "status": "OPEN",
            "transaction_count": 3,
            "combined_amount": Decimal("115000.00"),
            "reason": "Multiple transactions detected.",
            "transaction_ids": [
                "TXN-001",
                "TXN-002",
                "TXN-003",
            ],
        }

    def get_account(self, db, account_id):
        return {
            "account_id": "AI-ACC-1842",
            "bank_name": "AI Bank",
            "customer_name": "Arun Kumar",
            "currency": "INR",
        }

    def get_transactions(
        self,
        db,
        account_id,
        transaction_ids=None,
    ):
        assert account_id == "AI-ACC-1842"

        assert transaction_ids == [
            "TXN-001",
            "TXN-002",
            "TXN-003",
        ]

        return [
            {
                "transaction_id": "TXN-001",
                "amount": Decimal("40000.00"),
                "status": "SETTLED",
            },
            {
                "transaction_id": "TXN-002",
                "amount": Decimal("35000.00"),
                "status": "SETTLED",
            },
            {
                "transaction_id": "TXN-003",
                "amount": Decimal("40000.00"),
                "status": "SETTLED",
            },
        ]

    def get_aml_profile(self, db, account_id):
        return {
            "account_id": "AI-ACC-1842",
            "risk_category": "MEDIUM",
            "expected_max_transaction": Decimal("100000.00"),
            "expected_daily_transaction_count": 5,
            "expected_monthly_volume": Decimal("500000.00"),
            "baseline_window_days": 90,
        }


def test_investigator_agent_returns_structured_result():
    agent = InvestigatorAgent(
        tool_registry=FakeToolRegistry()
    )

    result = agent.investigate(
        db=None,
        alert_id="ALERT-001",
    )

    assert isinstance(result, InvestigatorResult)

    assert result.alert_id == "ALERT-001"
    assert result.account_id == "AI-ACC-1842"

    assert result.evidence.alert["rule_code"] == "STRUCTURING"
    assert result.evidence.account["customer_name"] == "Arun Kumar"

    assert len(result.evidence.transactions) == 3

    assert (
        result.evidence.aml_profile["risk_category"]
        == "MEDIUM"
    )