from app.agents.analysis_schema import AMLAnalysis
from app.agents.schemas import InvestigatorResult


class DeterministicInvestigator:

    def analyze(
        self,
        result: InvestigatorResult,
    ) -> AMLAnalysis:

        evidence = result.evidence
        alert = evidence.alert
        account = evidence.account
        profile = evidence.aml_profile
        transactions = evidence.transactions
        behavior = evidence.behavior

        findings = []

        if alert["rule_code"] == "STRUCTURING":
            findings.append(
                {
                    "code": "STRUCTURING_PATTERN",
                    "severity": (
                        alert["severity"].value
                        if hasattr(alert["severity"], "value")
                        else str(alert["severity"])
                    ),
                    "description": alert["reason"],
                    "evidence": [
                        f"Transaction count: {alert['transaction_count']}",
                        f"Combined amount: {alert['combined_amount']}",
                        f"Transaction IDs: {alert['transaction_ids']}",
                    ],
                }
            )

        if str(profile["risk_category"]) in {"MEDIUM", "HIGH"}:
            findings.append(
                {
                    "code": "CUSTOMER_RISK_CATEGORY",
                    "severity": str(profile["risk_category"]),
                    "description": (
                        "Customer has an elevated configured AML risk category."
                    ),
                    "evidence": [
                        f"Risk category: {profile['risk_category']}",
                        f"Baseline window: {profile['baseline_window_days']} days",
                    ],
                }
            )

        above_expected = [
            tx
            for tx in transactions
            if tx["amount"] > profile["expected_max_transaction"]
        ]

        if above_expected:
            findings.append(
                {
                    "code": "ABOVE_EXPECTED_TRANSACTION_SIZE",
                    "severity": "MEDIUM",
                    "description": (
                        "One or more transactions exceed the "
                        "configured expected maximum."
                    ),
                    "evidence": [
                        f"{tx['transaction_id']}: {tx['amount']}"
                        for tx in above_expected
                    ],
                }
            )

        behavior = evidence.behavior

        behavior_findings = behavior.get("findings", [])

        for finding in behavior_findings:
            findings.append(
                {
                    "code": finding.code,
                    "severity": finding.severity,
                    "description": finding.description,
                    "evidence": [
                        f"Title: {finding.title}",
                        f"Evidence: {finding.evidence}",
                    ],
                }
            )

        outcome = (
            "ESCALATE"
            if any(
                finding["code"] == "STRUCTURING_PATTERN"
                for finding in findings
            )
            else "REVIEW_REQUIRED"
            if findings
            else "NO_ADVERSE_FINDING"
        )

        return AMLAnalysis(
            alert_id=result.alert_id,
            account_id=result.account_id,
            customer_name=account["customer_name"],
            findings=findings,
            outcome=outcome,
        )