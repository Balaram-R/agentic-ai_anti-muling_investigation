from dataclasses import dataclass


@dataclass
class CriticResult:
    passed: bool
    issues: list[str]


class InvestigationCritic:
    def review(
        self,
        findings,
        policy_evidence,
        recommendation,
    ) -> CriticResult:

        issues = []

        # Every finding must have supporting evidence.
        for finding in findings:
            if not finding.evidence:
                issues.append(
                    f"Finding {finding.code} has no supporting evidence."
                )

        # Findings should have policy context.
        if findings and not policy_evidence:
            issues.append(
                "AML findings exist but no relevant policy evidence was retrieved."
            )

        # Escalation must remain subject to human approval.
        if (
            recommendation.action == "ESCALATE_FOR_REVIEW"
            and not recommendation.requires_human_approval
        ):
            issues.append(
                "Escalation recommendation does not require human approval."
            )

        # Recommendation must explain itself.
        if not recommendation.rationale.strip():
            issues.append(
                "Recommendation does not contain a rationale."
            )

        return CriticResult(
            passed=len(issues) == 0,
            issues=issues,
        )