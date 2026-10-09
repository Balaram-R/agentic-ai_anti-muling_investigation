from dataclasses import dataclass


@dataclass
class AMLFinding:
    code: str
    severity: str
    title: str
    description: str
    evidence: list[str]


class AMLEvidenceAnalyzer:

    def analyze(
        self,
        alert,
        account,
        aml_profile,
        transactions,
    ) -> list[AMLFinding]:

        findings: list[AMLFinding] = []

        if alert.rule_code == "STRUCTURING":
            findings.append(
                AMLFinding(
                    code="STRUCTURING_PATTERN",
                    severity=alert.severity.value,
                    title="Potential structuring pattern",
                    description=alert.reason,
                    evidence=[
                        f"Transaction count: {alert.transaction_count}",
                        f"Combined amount: {alert.combined_amount}",
                        "Monitoring window: 60 minutes",
                    ],
                )
            )

        transactions_above_expected_max = [
            tx
            for tx in transactions
            if tx.amount > aml_profile.expected_max_transaction
        ]

        if transactions_above_expected_max:
            findings.append(
                AMLFinding(
                    code="ABOVE_EXPECTED_TRANSACTION_SIZE",
                    severity="MEDIUM",
                    title="Transaction exceeds customer expected maximum",
                    description=(
                        "One or more transactions exceed the "
                        "customer's configured expected maximum transaction amount."
                    ),
                    evidence=[
                        f"Expected maximum: {aml_profile.expected_max_transaction}",
                        *[
                            f"{tx.transaction_id}: {tx.amount}"
                            for tx in transactions_above_expected_max
                        ],
                    ],
                )
            )

        if aml_profile.risk_category.value in {"MEDIUM", "HIGH"}:
            findings.append(
                AMLFinding(
                    code="CUSTOMER_RISK_CATEGORY",
                    severity=aml_profile.risk_category.value,
                    title="Customer has elevated AML risk category",
                    description=(
                        "The account's configured AML profile places the "
                        "customer in an elevated risk category."
                    ),
                    evidence=[
                        f"Risk category: {aml_profile.risk_category.value}",
                        f"Baseline window: {aml_profile.baseline_window_days} days",
                    ],
                )
            )

        return findings