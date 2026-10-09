from decimal import Decimal

from app.agents.analysis_schema import AMLAnalysis
from app.agents.llm_investigator import LLMInvestigator
from app.agents.schemas import (
    InvestigatorEvidence,
    InvestigatorResult,
)


class FakeLLMProvider:
    def analyze(self, system_prompt, user_prompt):
        return AMLAnalysis(
            alert_id="ALERT-001",
            account_id="AI-ACC-1842",
            customer_name="Arun Kumar",
            findings=[
                {
                    "code": "STRUCTURING_PATTERN",
                    "severity": "HIGH",
                    "description": "Multiple transactions were detected within the configured monitoring window.",
                    "evidence": [
                        "Transaction count: 3",
                        "Combined amount: 115000.00",
                    ],
                }
            ],
            outcome="ESCALATE",
        )


def test_llm_investigator_uses_provider():
    result = InvestigatorResult(
        alert_id="ALERT-001",
        account_id="AI-ACC-1842",
        evidence=InvestigatorEvidence(
            alert={
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
            },
            account={
                "account_id": "AI-ACC-1842",
                "customer_name": "Arun Kumar",
                "currency": "INR",
            },
            transactions=[
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
            ],
            aml_profile={
                "risk_category": "MEDIUM",
                "expected_max_transaction": Decimal("100000.00"),
                "baseline_window_days": 90,
            },
        ),
    )

    investigator = LLMInvestigator(
        provider=FakeLLMProvider()
    )

    analysis = investigator.analyze(result)

    assert isinstance(analysis, AMLAnalysis)

    assert analysis.alert_id == "ALERT-001"
    assert analysis.account_id == "AI-ACC-1842"
    assert analysis.customer_name == "Arun Kumar"

    assert len(analysis.findings) == 1
    assert analysis.findings[0].code == "STRUCTURING_PATTERN"
    assert analysis.findings[0].severity == "HIGH"

    assert analysis.outcome == "ESCALATE"