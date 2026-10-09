from decimal import Decimal

from app.agents.fallback_investigator import DeterministicInvestigator
from app.agents.schemas import (
    InvestigatorEvidence,
    InvestigatorResult,
)


def test_deterministic_investigator_handles_structuring_case():

    result = InvestigatorResult(
        alert_id="ALERT-001",
        account_id="AI-ACC-1842",
        evidence=InvestigatorEvidence(
            alert={
                "rule_code": "STRUCTURING",
                "severity": "HIGH",
                "reason": "Multiple transactions detected.",
                "transaction_count": 3,
                "combined_amount": Decimal("115000.00"),
                "transaction_ids": [
                    "TXN-001",
                    "TXN-002",
                    "TXN-003",
                ],
            },
            account={
                "customer_name": "Arun Kumar",
            },
            transactions=[
                {
                    "transaction_id": "TXN-001",
                    "amount": Decimal("40000.00"),
                },
                {
                    "transaction_id": "TXN-002",
                    "amount": Decimal("35000.00"),
                },
                {
                    "transaction_id": "TXN-003",
                    "amount": Decimal("40000.00"),
                },
            ],
            aml_profile={
                "risk_category": "MEDIUM",
                "expected_max_transaction": Decimal("100000.00"),
                "baseline_window_days": 90,
            },
        ),
    )

    investigator = DeterministicInvestigator()

    analysis = investigator.analyze(result)

    assert analysis.outcome == "ESCALATE"

    codes = [
        finding.code
        for finding in analysis.findings
    ]

    assert "STRUCTURING_PATTERN" in codes
    assert "CUSTOMER_RISK_CATEGORY" in codes
    assert "ABOVE_EXPECTED_TRANSACTION_SIZE" not in codes