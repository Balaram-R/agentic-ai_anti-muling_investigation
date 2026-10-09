from types import SimpleNamespace

from app.aml.recommendation import AMLRecommendationEngine


def test_structuring_assessment_requires_human_approval():
    assessment = SimpleNamespace(
        outcome="ESCALATE",
        rationale="Structuring pattern identified.",
        finding_codes=["STRUCTURING_PATTERN"],
    )

    engine = AMLRecommendationEngine()

    recommendation = engine.recommend(assessment)

    assert recommendation.action == "ESCALATE_FOR_REVIEW"
    assert recommendation.requires_human_approval is True