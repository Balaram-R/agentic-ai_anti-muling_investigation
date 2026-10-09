from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aml_alert import (
    AMLAlert,
    AMLAlertSeverity,
    AMLAlertStatus,
)
from app.models.aml_alert_transaction import AMLAlertTransaction


class AMLAlertService:

    def create_structuring_alert(
        self,
        db: Session,
        account_id: str,
        transaction_count: int,
        combined_amount: Decimal,
        reason: str,
        triggered_at: datetime,
        transaction_ids: list[str],
    ) -> AMLAlert:

        existing_alert = db.execute(
            select(AMLAlert)
            .where(
                AMLAlert.account_id == account_id,
                AMLAlert.rule_code == "STRUCTURING",
                AMLAlert.status.in_(
                    [
                        AMLAlertStatus.OPEN,
                        AMLAlertStatus.UNDER_REVIEW,
                    ]
                ),
            )
            .order_by(AMLAlert.triggered_at.desc())
        ).scalars().first()

        if existing_alert:
            return existing_alert

        alert = AMLAlert(
            alert_id=str(uuid4()),
            account_id=account_id,
            rule_code="STRUCTURING",
            severity=AMLAlertSeverity.HIGH,
            status=AMLAlertStatus.OPEN,
            triggered_at=triggered_at,
            transaction_count=transaction_count,
            combined_amount=combined_amount,
            reason=reason,
        )

        db.add(alert)
        db.flush()

        for transaction_id in transaction_ids:
            db.add(
                AMLAlertTransaction(
                    alert_id=alert.alert_id,
                    transaction_id=transaction_id,
                )
            )

        db.commit()
        db.refresh(alert)

        return alert
    def attach_transaction_evidence(
        self,
        db: Session,
        alert_id: str,
        transaction_ids: list[str],
    ) -> None:

        alert = db.get(AMLAlert, alert_id)

        if not alert:
            raise ValueError("AML alert not found")

        for transaction_id in transaction_ids:
            existing = db.execute(
                select(AMLAlertTransaction).where(
                    AMLAlertTransaction.alert_id == alert_id,
                    AMLAlertTransaction.transaction_id == transaction_id,
                )
            ).scalar_one_or_none()

            if not existing:
                db.add(
                    AMLAlertTransaction(
                        alert_id=alert_id,
                        transaction_id=transaction_id,
                    )
                )

        db.commit()