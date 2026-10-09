from decimal import Decimal
from types import SimpleNamespace

from app.agents.orchestrator import InvestigationOrchestrator
from app.agents.schemas import InvestigatorEvidence, InvestigatorResult
from app.aml.case_assessment import AMLCaseAssessmentEngine
from app.aml.recommendation import AMLRecommendationEngine


class FakeInvestigator:

    def investigate(
        self,
        db,
        alert_id,
        investigation_id=None,
    ):
        assert db is None
        assert alert_id == "ALERT-001"
        assert investigation_id is None

        return InvestigatorResult(
            alert_id=alert_id,
            account_id="AI-ACC-1842",
            evidence=InvestigatorEvidence(
                alert={
                    "alert_id": alert_id,
                    "account_id": "AI-ACC-1842",
                    "rule_code": "STRUCTURING",
                    "transaction_count": 3,
                    "combined_amount": Decimal("115000.00"),
                    "transaction_ids": [
                        "TXN-001",
                        "TXN-002",
                        "TXN-003",
                    ],
                },
                account={
                    "account_id": "AI-ACC-1842",
                    "customer_name": "Arun Kumar",
                },
                transactions=[],
                aml_profile={
                    "risk_category": "MEDIUM",
                },
            ),
        )


class FakeReasoningEngine:

    def analyze(self, evidence):
        return SimpleNamespace(
            findings=[
                SimpleNamespace(
                    code="STRUCTURING_PATTERN",
                    severity="HIGH",
                    title="Potential structuring pattern",
                    description="Multiple transactions detected.",
                    evidence=[
                        "Transaction count: 3",
                        "Combined amount: 115000.00",
                    ],
                )
            ]
        )


def test_orchestrator_runs_complete_investigation():

    orchestrator = InvestigationOrchestrator(
        investigator=FakeInvestigator(),
        reasoning_engine=FakeReasoningEngine(),
        assessment_engine=AMLCaseAssessmentEngine(),
        recommendation_engine=AMLRecommendationEngine(),
    )

    result = orchestrator.run(
        db=None,
        alert_id="ALERT-001",
    )

    assert result["alert_id"] == "ALERT-001"

    assert (
        result["analysis"].findings[0].code
        == "STRUCTURING_PATTERN"
    )

    assert result["assessment"].outcome == "ESCALATE"

    assert (
        result["recommendation"].action
        == "ESCALATE_FOR_REVIEW"
    )

    assert (
        result["recommendation"].requires_human_approval
        is True
    )