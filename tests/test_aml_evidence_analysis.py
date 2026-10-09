from decimal import Decimal
from types import SimpleNamespace

from app.aml.evidence_analysis import AMLEvidenceAnalyzer


def test_structuring_case_produces_expected_findings():
    alert = SimpleNamespace(
        rule_code="STRUCTURING",
        severity=SimpleNamespace(value="HIGH"),
        reason="3 outgoing settled transactions totaling 115000.00 occurred within 60 minutes.",
        transaction_count=3,
        combined_amount=Decimal("115000.00"),
    )

    account = SimpleNamespace(
        account_id="AI-ACC-1842",
    )

    aml_profile = SimpleNamespace(
        risk_category=SimpleNamespace(value="MEDIUM"),
        expected_max_transaction=Decimal("100000.00"),
        baseline_window_days=90,
    )

    transactions = [
        SimpleNamespace(
            transaction_id="TXN-9945AF44B8E4",
            amount=Decimal("40000.00"),
        ),
        SimpleNamespace(
            transaction_id="TXN-CD2EB6F5FE73",
            amount=Decimal("35000.00"),
        ),
        SimpleNamespace(
            transaction_id="TXN-94CA245A351A",
            amount=Decimal("40000.00"),
        ),
    ]

    analyzer = AMLEvidenceAnalyzer()

    findings = analyzer.analyze(
        alert=alert,
        account=account,
        aml_profile=aml_profile,
        transactions=transactions,
    )

    codes = {finding.code for finding in findings}

    assert "STRUCTURING_PATTERN" in codes
    assert "CUSTOMER_RISK_CATEGORY" in codes

    # None of the individual transactions exceeds ₹100,000.
    assert "ABOVE_EXPECTED_TRANSACTION_SIZE" not in codes

    structuring = next(
        finding
        for finding in findings
        if finding.code == "STRUCTURING_PATTERN"
    )

    assert structuring.severity == "HIGH"
    assert "115000.00" in structuring.description