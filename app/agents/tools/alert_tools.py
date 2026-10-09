from sqlalchemy.orm import Session

from app.repositories.aml_alerts import AMLAlertRepository


class AlertTools:
    def __init__(self):
        self.repository = AMLAlertRepository()

    def get_alert_evidence(self, db: Session, alert_id: str):
        alert = self.repository.get(db, alert_id)

        if not alert:
            raise ValueError(f"AML alert not found: {alert_id}")

        transaction_ids = self.repository.get_transaction_ids(
            db,
            alert_id,
        )

        return {
            "alert_id": alert.alert_id,
            "account_id": alert.account_id,
            "rule_code": alert.rule_code,
            "severity": alert.severity,
            "status": alert.status,
            "triggered_at": alert.triggered_at,
            "transaction_count": alert.transaction_count,
            "combined_amount": alert.combined_amount,
            "reason": alert.reason,
            "transaction_ids": transaction_ids,
        }