from dataclasses import dataclass


@dataclass
class AMLRecommendation:
    action: str
    rationale: str
    requires_human_approval: bool


class AMLRecommendationEngine:

    def recommend(self, assessment) -> AMLRecommendation:
        if assessment.outcome == "ESCALATE":
            return AMLRecommendation(
                action="ESCALATE_FOR_REVIEW",
                rationale=(
                    "The case assessment identified a structuring pattern. "
                    "The case should be escalated for human review."
                ),
                requires_human_approval=True,
            )

        if assessment.outcome == "REVIEW_REQUIRED":
            return AMLRecommendation(
                action="CONTINUE_REVIEW",
                rationale=(
                    "The case contains AML findings that require additional "
                    "investigation before a final decision."
                ),
                requires_human_approval=True,
            )

        return AMLRecommendation(
            action="NO_FURTHER_ACTION",
            rationale=(
                "No adverse AML findings were identified from the available "
                "evidence."
            ),
            requires_human_approval=True,
        )