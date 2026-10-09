from types import SimpleNamespace

from app.agents.tools.account_tools import AccountTools


class FakeAccountRepository:
    def get(self, db, account_id):
        if account_id == "AI-ACC-1842":
            return SimpleNamespace(
                account_id="AI-ACC-1842",
                bank_name="AI Bank",
                customer_name="Arun Kumar",
                account_number="AI-ACC-1842",
                balance=1500000,
                currency="INR",
            )

        return None


def test_get_account_returns_account_details():
    tools = AccountTools()

    tools.repository = FakeAccountRepository()

    result = tools.get_account(
        db=None,
        account_id="AI-ACC-1842",
    )

    assert result["account_id"] == "AI-ACC-1842"
    assert result["bank_name"] == "AI Bank"
    assert result["customer_name"] == "Arun Kumar"
    assert result["currency"] == "INR"


def test_get_account_raises_when_account_not_found():
    tools = AccountTools()

    tools.repository = FakeAccountRepository()

    try:
        tools.get_account(
            db=None,
            account_id="UNKNOWN-ACCOUNT",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Account not found: UNKNOWN-ACCOUNT"