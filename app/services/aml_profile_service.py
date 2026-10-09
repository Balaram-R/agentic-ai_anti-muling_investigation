from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.aml_profile import AMLProfile


class AMLProfileService:
    def get(self, db: Session, account_id: str) -> AMLProfile | None:
        return (
            db.query(AMLProfile)
            .join(Account, Account.account_id == AMLProfile.account_id)
            .filter(AMLProfile.account_id == account_id)
            .first()
        )