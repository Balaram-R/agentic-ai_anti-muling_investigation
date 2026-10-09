from types import SimpleNamespace

from app.agents.tools.transaction_tools import TransactionTools


class FakeTransactionRepository:
    def list_for_account(self, db, account_id):
        if account_id != "AI-ACC-1842":
            return []

        return [
            SimpleNamespace(
                transaction_id="TXN-TEST-001",
                transaction_type="TRANSFER",
                sender_account_id="AI-ACC-1842",
                receiver_account_id="BANKB-ACC-5276",
                amount=40000,
                currency="INR",
                purpose="GENERAL_TRANSFER",
                timestamp="2026-09-30T10:00:00Z",
                status="SETTLED",
            ),
            SimpleNamespace(
                transaction_id="TXN-TEST-002",
                transaction_type="TRANSFER",
                sender_account_id="AI-ACC-1842",
                receiver_account_id="BANKB-ACC-5276",
                amount=35000,
                currency="INR",
                purpose="GENERAL_TRANSFER",
                timestamp="2026-09-30T10:10:00Z",
                status="SETTLED",
            ),
        ]


def test_get_transactions_returns_transaction_evidence():
    tools = TransactionTools()
    tools.repository = FakeTransactionRepository()

    result = tools.get_transactions(
        db=None,
        account_id="AI-ACC-1842",
    )

    assert len(result) == 2
    assert result[0]["transaction_id"] == "TXN-TEST-001"
    assert result[0]["sender_account_id"] == "AI-ACC-1842"
    assert result[0]["receiver_account_id"] == "BANKB-ACC-5276"
    assert result[0]["amount"] == 40000
    assert result[0]["currency"] == "INR"
    assert result[0]["status"] == "SETTLED"


def test_get_transactions_respects_limit():
    tools = TransactionTools()
    tools.repository = FakeTransactionRepository()

    result = tools.get_transactions(
        db=None,
        account_id="AI-ACC-1842",
        limit=1,
    )

    assert len(result) == 1
    assert result[0]["transaction_id"] == "TXN-TEST-001"


def test_get_transactions_returns_empty_for_unknown_account():
    tools = TransactionTools()
    tools.repository = FakeTransactionRepository()

    result = tools.get_transactions(
        db=None,
        account_id="UNKNOWN-ACCOUNT",
    )

    assert result == []