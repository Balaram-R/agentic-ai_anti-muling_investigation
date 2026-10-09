from datetime import timedelta
from decimal import Decimal
from collections import defaultdict
from app.schemas.aml_behavior_summary import AMLBehaviorSummary

from sqlalchemy.orm import Session

from app.repositories.accounts import AccountRepository
from app.repositories.transactions import TransactionRepository
from app.models.aml_profile import AMLProfile
from app.aml.behavior_finding import AMLBehaviorFindingBuilder


class AMLBehaviorService:

    def __init__(
        self,
        accounts: AccountRepository,
        transactions: TransactionRepository,
    ):
        self.accounts = accounts
        self.transactions = transactions
        self.finding_builder = AMLBehaviorFindingBuilder()

    def get_behavior(
        self,
        db: Session,
        account_id: str,
    ):
    

        account_transactions = self.transactions.list_for_account(
            db,
            account_id,
        )

        aml_profile = db.get(AMLProfile, account_id)

        if not aml_profile:
            raise ValueError("AML profile not found")

        monthly_data = defaultdict(
            lambda: {
                "transaction_count": 0,
                "incoming": Decimal("0.00"),
                "outgoing": Decimal("0.00"),
            }
        )

        evidence = []

        for transaction in account_transactions:
            month = transaction.timestamp.strftime("%Y-%m")

            monthly_data[month]["transaction_count"] += 1

            if transaction.receiver_account_id == account_id:
                monthly_data[month]["incoming"] += transaction.amount

            if transaction.sender_account_id == account_id:
                monthly_data[month]["outgoing"] += transaction.amount

        monthly = []

        for month in sorted(monthly_data):
            data = monthly_data[month]

            monthly.append(
                {
                    "month": month,
                    "transaction_count": data["transaction_count"],
                    "incoming": f"{data['incoming']:.2f}",
                    "outgoing": f"{data['outgoing']:.2f}",
                }
            )

        outgoing_transactions = sorted(
            [
                transaction
                for transaction in account_transactions
                if transaction.sender_account_id == account_id
            ],
            key=lambda transaction: transaction.timestamp,
        )

        rapid_transfer_detected = False
        rapid_transactions = []

        for i in range(len(outgoing_transactions)):
            window_start = outgoing_transactions[i].timestamp
            window_transactions = []

            for j in range(i, len(outgoing_transactions)):
                if (
                    outgoing_transactions[j].timestamp - window_start
                    <= timedelta(seconds=60)
                ):
                    window_transactions.append(
                        outgoing_transactions[j]
                    )
                else:
                    break

            if len(window_transactions) >= 3:
                rapid_transfer_detected = True
                rapid_transactions = window_transactions
                break

        evidence = []

        if rapid_transfer_detected:
            rapid_total = sum(
                transaction.amount
                for transaction in rapid_transactions
            )

            evidence.append(
                {
                    "code": "RAPID_OUTGOING_TRANSFERS",
                    "message": "Multiple rapid outgoing transfers detected",
                    "details": {
                        "transaction_count": len(rapid_transactions),
                        "window_seconds": 60,
                        "total_amount": f"{rapid_total:.2f}",
                        "transaction_ids": [
                            transaction.transaction_id
                            for transaction in rapid_transactions
                        ],
                        "transactions": [
                            {
                                "transaction_id": transaction.transaction_id,
                                "timestamp": transaction.timestamp.isoformat(),
                                "amount": f"{transaction.amount:.2f}",
                                "counterparty_account_id": transaction.receiver_account_id,
                            }
                            for transaction in rapid_transactions
                        ],
                    },
                }
            )

        if aml_profile.expected_monthly_volume is not None:
            for month_data in monthly:
                actual_outgoing = Decimal(month_data["outgoing"])

                if actual_outgoing > aml_profile.expected_monthly_volume:
                    evidence.append(
                        {
                            "code": "MONTHLY_VOLUME_ABOVE_BASELINE",
                            "message": "Activity exceeded the customer's configured monthly baseline",
                            "details": {
                                "month": month_data["month"],
                                "actual_outgoing": f"{actual_outgoing:.2f}",
                                "expected_monthly_volume": f"{aml_profile.expected_monthly_volume:.2f}",
                            },
                        }
                    )
                    break

        if len(monthly) >= 2:
            first = monthly[0]
            last = monthly[-1]

            if last["transaction_count"] > first["transaction_count"]:
                evidence.append(
                    {
                        "code": "TRANSACTION_FREQUENCY_INCREASED",
                        "message": "Transaction frequency increased over time",
                        "details": {
                            "previous_month": first["month"],
                            "previous_count": first["transaction_count"],
                            "current_month": last["month"],
                            "current_count": last["transaction_count"],
                        },
                    }
                )

            if Decimal(last["outgoing"]) > Decimal(first["outgoing"]):
                evidence.append(
                    {
                        "code": "OUTGOING_VOLUME_INCREASED",
                        "message": "Outgoing volume increased over time",
                        "details": {
                            "previous_month": first["month"],
                            "previous_outgoing": first["outgoing"],
                            "current_month": last["month"],
                            "current_outgoing": last["outgoing"],
                        },
                    }
                )

        unique_counterparties = set()

        for transaction in account_transactions:
            if transaction.sender_account_id == account_id:
                unique_counterparties.add(
                    transaction.receiver_account_id
                )

            if transaction.receiver_account_id == account_id:
                unique_counterparties.add(
                    transaction.sender_account_id
                )

        if len(unique_counterparties) > 1:
            evidence.append(
                {
                    "code": "MULTIPLE_COUNTERPARTIES",
                    "message": "Funds were exchanged with multiple counterparties",
                    "details": {
                        "counterparty_count": len(unique_counterparties),
                        "counterparties": sorted(unique_counterparties),
                    },
                }
            )

        if not evidence:
            evidence.append(
                {
                    "code": "NO_SIGNIFICANT_INDICATOR",
                    "message": "No significant behavioral indicator identified from available transaction data",
                    "details": {},
                }
            )

        findings = self.finding_builder.build(evidence)

        severity_order = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }

        highest_severity = None

        if findings:
            highest_severity = max(
                findings,
                key=lambda finding: severity_order.get(
                    finding.severity,
                    0,
                ),
            ).severity

        summary = AMLBehaviorSummary(
            finding_count=len(findings),
            highest_severity=highest_severity,
        )

        return {
            "account_id": account_id,
            "monthly": monthly,
            "evidence": evidence,
            "findings": findings,
            "summary": summary,
        }