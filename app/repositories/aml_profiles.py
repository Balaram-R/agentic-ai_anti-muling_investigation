from sqlalchemy.orm import Session

from app.models.aml_profile import AMLProfile


class AMLProfileRepository:
    def get(self, db: Session, account_id: str) -> AMLProfile | None:
        return db.get(AMLProfile, account_id)
