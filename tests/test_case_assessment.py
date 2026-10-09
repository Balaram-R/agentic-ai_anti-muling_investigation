from app.aml.case_assessment import AMLCaseAssessmentEngine
from app.aml.evidence_analysis import AMLFinding


def test_structuring_case_is_assessed_for_escalation():
    findings = [
        AMLFinding(
            code="STRUCTURING_PATTERN",
            severity="HIGH",
            title="Potential structuring pattern",
            description="Multiple transactions detected.",
            evidence=[
                "Transaction count: 3",
                "Combined amount: 115000.00",
            ],
        ),
        AMLFinding(
            code="CUSTOMER_RISK_CATEGORY",
            severity="MEDIUM",
            title="Customer has elevated AML risk category",
            description="Customer risk category is MEDIUM.",
            evidence=[
                "Risk category: MEDIUM",
            ],
        ),
    ]

    engine = AMLCaseAssessmentEngine()

    assessment = engine.assess(findings)

    assert assessment.outcome == "ESCALATE"
    assert "STRUCTURING_PATTERN" in assessment.finding_codes