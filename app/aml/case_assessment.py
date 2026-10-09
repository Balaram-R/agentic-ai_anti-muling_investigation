from dataclasses import dataclass


@dataclass
class AMLCaseAssessment:
    outcome: str
    rationale: str
    finding_codes: list[str]


class AMLCaseAssessmentEngine:

    def assess(self, findings) -> AMLCaseAssessment:
        finding_codes = [finding.code for finding in findings]

        if "STRUCTURING_PATTERN" in finding_codes:
            return AMLCaseAssessment(
                outcome="ESCALATE",
                rationale=(
                    "The investigation identified a potential structuring "
                    "pattern supported by multiple transactions within the "
                    "configured monitoring window."
                ),
                finding_codes=finding_codes,
            )

        if findings:
            return AMLCaseAssessment(
                outcome="REVIEW_REQUIRED",
                rationale=(
                    "The investigation identified AML findings that require "
                    "further review."
                ),
                finding_codes=finding_codes,
            )

        return AMLCaseAssessment(
            outcome="NO_ADVERSE_FINDING",
            rationale=(
                "No configured AML findings were identified from the "
                "available evidence."
            ),
            finding_codes=[],
        )