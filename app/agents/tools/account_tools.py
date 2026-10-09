from sqlalchemy.orm import Session

from app.repositories.accounts import AccountRepository


class AccountTools:
    def __init__(self):
        self.repository = AccountRepository()

    def get_account(self, db: Session, account_id: str):
        account = self.repository.get(db, account_id)

        if not account:
            raise ValueError(f"Account not found: {account_id}")

        return {
            "account_id": account.account_id,
            "bank_name": account.bank_name,
            "customer_name": account.customer_name,
            "account_number": account.account_number,
            "balance": account.balance,
            "currency": account.currency,
        }