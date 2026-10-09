from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aml_investigation import (
    AMLInvestigation,
    InvestigationStatus,
)


class AMLInvestigationRepository:

    def get(
        self,
        db: Session,
        investigation_id: str,
    ) -> AMLInvestigation | None:
        return db.get(AMLInvestigation, investigation_id)

    def get_by_alert(
        self,
        db: Session,
        alert_id: str,
    ) -> AMLInvestigation | None:
        return db.execute(
            select(AMLInvestigation).where(
                AMLInvestigation.alert_id == alert_id
            )
        ).scalar_one_or_none()

    def list_open(
        self,
        db: Session,
    ) -> list[AMLInvestigation]:
        return list(
            db.execute(
                select(AMLInvestigation)
                .where(
                    AMLInvestigation.status.in_(
                        [
                            InvestigationStatus.OPEN,
                            InvestigationStatus.IN_PROGRESS,
                        ]
                    )
                )
                .order_by(
                    AMLInvestigation.opened_at.desc()
                )
            ).scalars()
        )

    def create(
        self,
        db: Session,
        investigation: AMLInvestigation,
    ) -> AMLInvestigation:
        db.add(investigation)
        db.commit()
        db.refresh(investigation)
        return investigation

    def update(
        self,
        db: Session,
        investigation: AMLInvestigation,
    ) -> AMLInvestigation:
        db.flush()
        return investigation