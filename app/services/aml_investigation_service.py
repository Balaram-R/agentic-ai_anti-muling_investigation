from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.aml_investigation import (
    AMLInvestigation,
    InvestigationStatus,
)
from app.repositories.aml_investigations import (
    AMLInvestigationRepository,
)


class AMLInvestigationService:

    def __init__(
        self,
        repository: AMLInvestigationRepository,
    ):
        self.repository = repository

    def get(
        self,
        db: Session,
        investigation_id: str,
    ) -> AMLInvestigation | None:
        return self.repository.get(
            db,
            investigation_id,
        )

    def create(
        self,
        db: Session,
        alert_id: str,
        assigned_to: str | None = None,
    ) -> AMLInvestigation:

        existing = self.repository.get_by_alert(
            db,
            alert_id,
        )

        if existing:
            raise ValueError(
                "An investigation already exists for this AML alert"
            )

        investigation = AMLInvestigation(
            investigation_id=str(uuid4()),
            alert_id=alert_id,
            assigned_to=assigned_to,
            status=InvestigationStatus.OPEN,
            opened_at=datetime.now().astimezone(),
        )

        return self.repository.create(
            db,
            investigation,
        )

    def update_status(
        self,
        db: Session,
        investigation: AMLInvestigation,
        new_status: InvestigationStatus,
        conclusion: str | None = None,
    ) -> AMLInvestigation:

        if investigation.status == InvestigationStatus.COMPLETED:
            raise ValueError(
                "Completed investigations cannot be modified"
            )

        if new_status == InvestigationStatus.OPEN:
            if investigation.status != InvestigationStatus.IN_PROGRESS:
                raise ValueError(
                    "Only IN_PROGRESS investigations can return to OPEN"
                )

        elif new_status == InvestigationStatus.IN_PROGRESS:
            if investigation.status != InvestigationStatus.OPEN:
                raise ValueError(
                    "Only OPEN investigations can move to IN_PROGRESS"
                )

        elif new_status == InvestigationStatus.COMPLETED:
            if investigation.status != InvestigationStatus.IN_PROGRESS:
                raise ValueError(
                    "Only IN_PROGRESS investigations can be completed"
                )

            if not conclusion or not conclusion.strip():
                raise ValueError(
                    "A conclusion is required to complete an investigation"
                )

            investigation.closed_at = datetime.now().astimezone()
            investigation.conclusion = conclusion.strip()

        investigation.status = new_status

        return self.repository.update(
            db,
            investigation,
        )

    def save_analysis(
        self,
        db: Session,
        investigation: AMLInvestigation,
        analysis_result: dict,
    ) -> AMLInvestigation:
        investigation.analysis_result = analysis_result
        investigation.analysis_completed_at = datetime.now().astimezone()

        db.flush()

        return investigation