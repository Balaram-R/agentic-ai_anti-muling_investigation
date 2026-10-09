from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionStatus


@dataclass
class StructuringResult:
    triggered: bool
    transaction_count: int
    combined_amount: Decimal
    window_minutes: int
    transaction_ids: list[str]
    reason: str


class StructuringDetector:
    WINDOW_MINUTES = 60
    MIN_TRANSACTIONS = 3
    COMBINED_AMOUNT_THRESHOLD = Decimal("100000.00")

    def detect(
        self,
        db: Session,
        account_id: str,
        reference_time: datetime | None = None,
    ) -> StructuringResult:

        if reference_time is None:
            reference_time = datetime.now().astimezone()

        window_start = reference_time - timedelta(
            minutes=self.WINDOW_MINUTES
        )

        transactions = list(
            db.execute(
                select(Transaction)
                .where(
                    Transaction.sender_account_id == account_id,
                    Transaction.status == TransactionStatus.SETTLED,
                    Transaction.timestamp >= window_start,
                    Transaction.timestamp <= reference_time,
                )
                .order_by(Transaction.timestamp.asc())
            ).scalars()
        )

        transaction_count = len(transactions)
        combined_amount = sum(
            (tx.amount for tx in transactions),
            Decimal("0.00"),
        )

        triggered = (
            transaction_count >= self.MIN_TRANSACTIONS
            and combined_amount > self.COMBINED_AMOUNT_THRESHOLD
        )

        transaction_ids = [
            tx.transaction_id for tx in transactions
        ]

        if triggered:
            reason = (
                f"{transaction_count} outgoing settled transactions "
                f"totaling {combined_amount} occurred within "
                f"{self.WINDOW_MINUTES} minutes."
            )
        else:
            reason = "No structuring pattern detected."

        return StructuringResult(
            triggered=triggered,
            transaction_count=transaction_count,
            combined_amount=combined_amount,
            window_minutes=self.WINDOW_MINUTES,
            transaction_ids=transaction_ids,
            reason=reason,
        )