from sqlalchemy.orm import Session

from app.repositories.transactions import TransactionRepository


class TransactionTools:
    def __init__(self):
        self.repository = TransactionRepository()

    def get_transactions(
        self,
        db: Session,
        account_id: str,
        limit: int = 50,
        transaction_ids: list[str] | None = None,
    ):
        transactions = self.repository.list_for_account(
            db,
            account_id,
        )

        if transaction_ids is not None:
            transaction_id_set = set(transaction_ids)

            transactions = [
                tx
                for tx in transactions
                if tx.transaction_id in transaction_id_set
            ]

        transactions = transactions[:limit]

        return [
            {
                "transaction_id": tx.transaction_id,
                "transaction_type": tx.transaction_type,
                "sender_account_id": tx.sender_account_id,
                "receiver_account_id": tx.receiver_account_id,
                "amount": tx.amount,
                "currency": tx.currency,
                "purpose": tx.purpose,
                "timestamp": tx.timestamp,
                "status": tx.status,
            }
            for tx in transactions
        ]