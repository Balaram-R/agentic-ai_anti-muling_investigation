from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.aml_alert_event import AMLAlertEvent


class AMLAlertEventService:

    def record(
        self,
        db: Session,
        alert_id: str,
        event_type: str,
        description: str,
        old_status: str | None = None,
        new_status: str | None = None,
    ):
        event = AMLAlertEvent(
            event_id=str(uuid4()),
            alert_id=alert_id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            event_time=datetime.now().astimezone(),
            description=description,
        )

        db.add(event)
        db.flush()

        return event