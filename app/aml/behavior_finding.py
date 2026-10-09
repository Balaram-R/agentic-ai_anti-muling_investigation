from app.schemas.aml_behavior_finding import AMLBehaviorFinding


class AMLBehaviorFindingBuilder:

    def build(self, evidence: list[dict]) -> list[AMLBehaviorFinding]:
        findings = []

        for item in evidence:
            code = item["code"]

            if code == "RAPID_OUTGOING_TRANSFERS":
                findings.append(
                    AMLBehaviorFinding(
                        code=code,
                        severity="MEDIUM",
                        title="Rapid outgoing transfers",
                        description=(
                            "Multiple outgoing transfers occurred "
                            "within a short time window."
                        ),
                        evidence=item["details"],
                    )
                )

            elif code == "MONTHLY_VOLUME_ABOVE_BASELINE":
                findings.append(
                    AMLBehaviorFinding(
                        code=code,
                        severity="MEDIUM",
                        title="Monthly outgoing volume above baseline",
                        description=(
                            "Observed outgoing transaction volume "
                            "exceeded the customer's configured monthly baseline."
                        ),
                        evidence=item["details"],
                    )
                )

            elif code == "TRANSACTION_FREQUENCY_INCREASED":
                findings.append(
                    AMLBehaviorFinding(
                        code=code,
                        severity="MEDIUM",
                        title="Transaction frequency increased",
                        description=(
                            "Transaction frequency increased compared "
                            "with the earlier observed month."
                        ),
                        evidence=item["details"],
                    )
                )

            elif code == "OUTGOING_VOLUME_INCREASED":
                findings.append(
                    AMLBehaviorFinding(
                        code=code,
                        severity="MEDIUM",
                        title="Outgoing volume increased",
                        description=(
                            "Outgoing transaction volume increased "
                            "compared with the earlier observed month."
                        ),
                        evidence=item["details"],
                    )
                )

            elif code == "MULTIPLE_COUNTERPARTIES":
                findings.append(
                    AMLBehaviorFinding(
                        code=code,
                        severity="LOW",
                        title="Multiple counterparties",
                        description=(
                            "Funds were exchanged with multiple counterparties "
                            "during the observed period."
                        ),
                        evidence=item["details"],
                    )
                )

        return findings