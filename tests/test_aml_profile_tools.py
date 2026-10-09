from decimal import Decimal
from types import SimpleNamespace

from app.agents.tools.aml_profile_tools import AMLProfileTools


class FakeAMLProfileRepository:
    def get(self, db, account_id):
        if account_id != "AI-ACC-1842":
            return None

        return SimpleNamespace(
            account_id="AI-ACC-1842",
            risk_category="MEDIUM",
            expected_min_transaction=Decimal("10000.00"),
            expected_max_transaction=Decimal("100000.00"),
            expected_daily_transaction_count=5,
            expected_monthly_volume=Decimal("500000.00"),
            baseline_window_days=90,
        )


def test_get_aml_profile_returns_profile():
    tools = AMLProfileTools()
    tools.repository = FakeAMLProfileRepository()

    result = tools.get_aml_profile(
        db=None,
        account_id="AI-ACC-1842",
    )

    assert result["account_id"] == "AI-ACC-1842"
    assert result["risk_category"] == "MEDIUM"
    assert result["expected_min_transaction"] == Decimal("10000.00")
    assert result["expected_max_transaction"] == Decimal("100000.00")
    assert result["expected_daily_transaction_count"] == 5
    assert result["expected_monthly_volume"] == Decimal("500000.00")
    assert result["baseline_window_days"] == 90


def test_get_aml_profile_raises_when_not_found():
    tools = AMLProfileTools()
    tools.repository = FakeAMLProfileRepository()

    try:
        tools.get_aml_profile(
            db=None,
            account_id="UNKNOWN-ACCOUNT",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "AML profile not found: UNKNOWN-ACCOUNT"