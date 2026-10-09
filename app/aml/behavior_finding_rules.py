from app.schemas.aml_behavior_finding import AMLBehaviorFinding
from app.aml.behavior_finding_rules import FINDING_RULES


class AMLBehaviorFindingBuilder:

    def build(self, evidence: list[dict]) -> list[AMLBehaviorFinding]:
        findings = []

        for item in evidence:
            code = item["code"]

            rule = FINDING_RULES.get(code)

            if not rule:
                continue

            findings.append(
                AMLBehaviorFinding(
                    code=code,
                    severity=rule["severity"],
                    title=rule["title"],
                    description=rule["description"],
                    evidence=item["details"],
                )
            )

        return findings