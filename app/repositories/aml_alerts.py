from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.aml_alert import AMLAlert, AMLAlertStatus


class AMLAlertRepository:

    def get(self, db: Session, alert_id: str) -> AMLAlert | None:
        return db.get(AMLAlert, alert_id)

    def list_open(self, db: Session) -> list[AMLAlert]:
        return list(
            db.execute(
                select(AMLAlert)
                .where(AMLAlert.status == "OPEN")
                .order_by(AMLAlert.triggered_at.desc())
            ).scalars()
        )

    def list_for_account(
        self,
        db: Session,
        account_id: str,
    ) -> list[AMLAlert]:
        return list(
            db.execute(
                select(AMLAlert)
                .where(AMLAlert.account_id == account_id)
                .order_by(AMLAlert.triggered_at.desc())
            ).scalars()
        )
    def get_transaction_ids(
        self,
        db: Session,
        alert_id: str,
    ) -> list[str]:
        from app.models.aml_alert_transaction import AMLAlertTransaction

        return list(
            db.execute(
                select(AMLAlertTransaction.transaction_id)
                .where(
                    AMLAlertTransaction.alert_id == alert_id
                )
                .order_by(AMLAlertTransaction.transaction_id)
            ).scalars()
        )

    def update_status(
        self,
        db,
        alert,
        status,
    ):
        alert.status = status
        db.flush()
        return alert