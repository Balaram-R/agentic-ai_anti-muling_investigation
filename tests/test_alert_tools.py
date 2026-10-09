from decimal import Decimal
from types import SimpleNamespace

from app.agents.tools.alert_tools import AlertTools


class FakeAMLAlertRepository:
    def get(self, db, alert_id):
        if alert_id != "ALERT-001":
            return None

        return SimpleNamespace(
            alert_id="ALERT-001",
            account_id="AI-ACC-1842",
            rule_code="STRUCTURING",
            severity="HIGH",
            status="CLOSED",
            triggered_at="2026-09-30T10:00:00Z",
            transaction_count=3,
            combined_amount=Decimal("115000.00"),
            reason="3 outgoing settled transactions totaling 115000.00 occurred within 60 minutes.",
        )

    def get_transaction_ids(self, db, alert_id):
        return [
            "TXN-9945AF44B8E4",
            "TXN-CD2EB6F5FE73",
            "TXN-94CA245A351A",
        ]


def test_get_alert_evidence_returns_alert_and_transactions():
    tools = AlertTools()
    tools.repository = FakeAMLAlertRepository()

    result = tools.get_alert_evidence(
        db=None,
        alert_id="ALERT-001",
    )

    assert result["alert_id"] == "ALERT-001"
    assert result["account_id"] == "AI-ACC-1842"
    assert result["rule_code"] == "STRUCTURING"
    assert result["severity"] == "HIGH"
    assert result["transaction_count"] == 3
    assert result["combined_amount"] == Decimal("115000.00")

    assert result["transaction_ids"] == [
        "TXN-9945AF44B8E4",
        "TXN-CD2EB6F5FE73",
        "TXN-94CA245A351A",
    ]


def test_get_alert_evidence_raises_when_not_found():
    tools = AlertTools()
    tools.repository = FakeAMLAlertRepository()

    try:
        tools.get_alert_evidence(
            db=None,
            alert_id="UNKNOWN-ALERT",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "AML alert not found: UNKNOWN-ALERT"