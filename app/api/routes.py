import os
from app.agents.groq_provider import GroqLLMProvider
import logging
from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.agents.orchestrator import InvestigationOrchestrator
from app.repositories.accounts import AccountRepository
from app.repositories.transactions import TransactionRepository
from app.schemas.aml_profile import AMLProfileRead
from app.services.aml_profile_service import AMLProfileService
from app.services.aml_alert_service import AMLAlertService
from app.schemas.account import AccountRead
from app.schemas.transaction import TransactionCreate,TransactionRead
from app.services.transaction_service import TransactionService,TransactionServiceError
from app.aml.structuring import StructuringDetector
from app.repositories.aml_alerts import AMLAlertRepository
from app.models.aml_alert import AMLAlertStatus
from app.services.aml_alert_event_service import AMLAlertEventService
from app.services.agent_execution_service import AgentExecutionService
from app.models.aml_alert_event import AMLAlertEvent
from app.models.aml_alert_transaction import AMLAlertTransaction
from app.models.transaction import Transaction
from app.aml.case_assessment import AMLCaseAssessmentEngine
from app.schemas.aml_investigation import AMLInvestigationCaseRead
from app.aml.recommendation import AMLRecommendationEngine
from app.schemas.aml_behavior import AMLBehaviorRead
from app.schemas.aml_alert import (
    AMLAlertRead,
    AMLAlertDetailRead,
    AMLAlertStatusUpdate,
)
from pydantic import BaseModel, ConfigDict
from app.repositories.aml_investigations import AMLInvestigationRepository
from app.models.aml_profile import AMLProfile
from app.schemas.aml_profile import AMLProfileRead
from app.core.config import get_settings
from app.schemas.aml_investigation import (
    AMLInvestigationRead,
    AMLInvestigationCreate,
    AMLInvestigationStatusUpdate,
)
from app.services.aml_investigation_service import AMLInvestigationService
from app.models.aml_investigation import InvestigationStatus
from app.aml.evidence_analysis import AMLEvidenceAnalyzer
from app.aml.behavior_finding import AMLBehaviorFindingBuilder
from app.services.aml_behavior_service import AMLBehaviorService
agent_execution_service = AgentExecutionService()
aml_investigations = AMLInvestigationRepository()
aml_investigation_service = AMLInvestigationService(
    aml_investigations
)
evidence_analyzer = AMLEvidenceAnalyzer()
case_assessment_engine = AMLCaseAssessmentEngine()
recommendation_engine = AMLRecommendationEngine()

settings = get_settings()

groq_provider = GroqLLMProvider(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
)

investigation_orchestrator = InvestigationOrchestrator(
    llm_provider=groq_provider,
)
aml_alert_event_service = AMLAlertEventService()
aml_alerts = AMLAlertRepository()
aml_alert_service = AMLAlertService()
router=APIRouter(); accounts=AccountRepository(); transactions=TransactionRepository(); service=TransactionService(accounts,transactions); logger=logging.getLogger(__name__)
structuring_detector = StructuringDetector()
behavior_finding_builder = AMLBehaviorFindingBuilder()
aml_profile_service=AMLProfileService()
evidence_analyzer = AMLEvidenceAnalyzer()
case_assessment_engine = AMLCaseAssessmentEngine()
aml_behavior_service = AMLBehaviorService(
    accounts,
    transactions,
)

@router.get(
    "/accounts/{account_id}/aml/behavior",
    response_model=AMLBehaviorRead,
)
def account_aml_behavior(
    account_id: str,
    db: Session = Depends(get_db),
):
    if not accounts.get(db, account_id):
        raise HTTPException(404, "Account not found")

    try:
        return aml_behavior_service.get_behavior(
            db,
            account_id,
        )
    except ValueError as e:
        raise HTTPException(404, str(e)) from e
         
@router.get("/health")
def health(): return {"status":"ok"}
@router.post("/transactions",response_model=TransactionRead,status_code=201)
def create(req:TransactionCreate,db:Session=Depends(get_db)):
    try:
        t=service.create(db,req); db.commit(); db.refresh(t); return t
    except TransactionServiceError as e: db.rollback(); raise HTTPException(e.status_code,str(e)) from e
    except Exception: db.rollback(); logger.exception("transaction failure"); raise
@router.get("/transactions",response_model=list[TransactionRead])
def all_transactions(db:Session=Depends(get_db)): return transactions.list_all(db)
@router.get("/transactions/{transaction_id}",response_model=TransactionRead)
def one(transaction_id:str,db:Session=Depends(get_db)):
    t=transactions.get(db,transaction_id)
    if not t: raise HTTPException(404,"Transaction not found")
    return t
@router.get("/accounts/{account_id}",response_model=AccountRead)
def account(account_id:str,db:Session=Depends(get_db)):
    a=accounts.get(db,account_id)
    if not a: raise HTTPException(404,"Account not found")
    return a
@router.get("/accounts/{account_id}/transactions",response_model=list[TransactionRead])
def account_transactions(account_id:str,db:Session=Depends(get_db)):
    if not accounts.get(db,account_id): raise HTTPException(404,"Account not found")
    return transactions.list_for_account(db,account_id)
@router.get("/accounts/{account_id}/aml-profile", response_model=AMLProfileRead)
def account_aml_profile(account_id: str, db: Session = Depends(get_db)):
    profile = aml_profile_service.get(db, account_id)

    if not profile:
        raise HTTPException(404, "AML profile not found")

    return {
        "account_id": profile.account_id,
        "customer_name": profile.account.customer_name,
        "risk_category": profile.risk_category,
        "expected_min_transaction": profile.expected_min_transaction,
        "expected_max_transaction": profile.expected_max_transaction,
        "expected_daily_transaction_count": profile.expected_daily_transaction_count,
        "expected_monthly_volume": profile.expected_monthly_volume,
        "baseline_window_days": profile.baseline_window_days,
    }
@router.get("/accounts/{account_id}/aml/structuring")
def check_structuring(
    account_id: str,
    db: Session = Depends(get_db),
):
    if not accounts.get(db, account_id):
        raise HTTPException(404, "Account not found")

    result = structuring_detector.detect(db, account_id)

    alert = None

    if result.triggered:
        alert = aml_alert_service.create_structuring_alert(
            db=db,
            account_id=account_id,
            transaction_count=result.transaction_count,
            combined_amount=result.combined_amount,
            reason=result.reason,
            triggered_at=datetime.now().astimezone(),
            transaction_ids=result.transaction_ids,
        )
        
        db.commit()
        db.refresh(alert)

    return {
        "account_id": account_id,
        "rule": "STRUCTURING",
        "triggered": result.triggered,
        "transaction_count": result.transaction_count,
        "combined_amount": result.combined_amount,
        "window_minutes": result.window_minutes,
        "transaction_ids": result.transaction_ids,
        "reason": result.reason,
        "alert_id": alert.alert_id if alert else None,
        "alert_status": alert.status if alert else None,
    }
@router.get("/aml/alerts", response_model=list[AMLAlertRead])
def open_aml_alerts(db: Session = Depends(get_db)):
    return aml_alerts.list_open(db)


@router.get(
    "/accounts/{account_id}/aml/alerts",
    response_model=list[AMLAlertRead],
)
def account_aml_alerts(
    account_id: str,
    db: Session = Depends(get_db),
):
    if not accounts.get(db, account_id):
        raise HTTPException(404, "Account not found")

    return aml_alerts.list_for_account(db, account_id)
@router.get(
    "/aml/alerts/{alert_id}",
    response_model=AMLAlertDetailRead,
)
def get_aml_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    alert = aml_alerts.get(db, alert_id)

    if not alert:
        raise HTTPException(404, "AML alert not found")

    transaction_ids = aml_alerts.get_transaction_ids(
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

@router.patch(
    "/aml/alerts/{alert_id}/status",
    response_model=AMLAlertRead,
)
def update_aml_alert_status(
    alert_id: str,
    request: AMLAlertStatusUpdate,
    db: Session = Depends(get_db),
):
    alert = aml_alerts.get(db, alert_id)

    if not alert:
        raise HTTPException(404, "AML alert not found")

    if alert.status == AMLAlertStatus.CLOSED:
        raise HTTPException(
            400,
            "Closed AML alerts cannot be reopened or modified",
        )

    if request.status == AMLAlertStatus.OPEN:
        if alert.status != AMLAlertStatus.UNDER_REVIEW:
            raise HTTPException(
                400,
                "Only UNDER_REVIEW alerts can return to OPEN",
            )

    if request.status == AMLAlertStatus.UNDER_REVIEW:
        if alert.status != AMLAlertStatus.OPEN:
            raise HTTPException(
                400,
                "Only OPEN alerts can move to UNDER_REVIEW",
            )

    if request.status == AMLAlertStatus.CLOSED:
        if alert.status != AMLAlertStatus.UNDER_REVIEW:
            raise HTTPException(
                400,
                "Only UNDER_REVIEW alerts can be closed",
            )

    old_status = alert.status

    updated_alert = aml_alerts.update_status(
        db,
        alert,
        request.status,
    )

    aml_alert_event_service.record(
        db=db,
        alert_id=alert.alert_id,
        event_type="STATUS_CHANGED",
        old_status=old_status.value,
        new_status=request.status.value,
        description=(
            f"AML alert status changed from "
            f"{old_status.value} to {request.status.value}."
        ),
    )

    db.commit()
    db.refresh(updated_alert)

    return updated_alert

@router.get(
    "/aml/alerts/{alert_id}/investigation",
    response_model=AMLInvestigationRead,
)
def get_aml_investigation_by_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    investigation = aml_investigations.get_by_alert(
        db,
        alert_id,
    )

    if not investigation:
        raise HTTPException(
            404,
            "AML investigation not found",
        )

    return investigation


@router.post(
    "/aml/alerts/{alert_id}/investigation",
    response_model=AMLInvestigationRead,
    status_code=201,
)
def create_aml_investigation(
    alert_id: str,
    request: AMLInvestigationCreate,
    db: Session = Depends(get_db),
):
    alert = aml_alerts.get(db, alert_id)

    if not alert:
        raise HTTPException(
            404,
            "AML alert not found",
        )


    try:
        investigation = aml_investigation_service.create(
            db=db,
            alert_id=alert_id,
            assigned_to=request.assigned_to,
        )

        # An investigation has now started.
        # Move the alert from OPEN to UNDER_REVIEW.
        old_status = alert.status

        updated_alert = aml_alerts.update_status(
            db,
            alert,
            AMLAlertStatus.UNDER_REVIEW,
        )

        aml_alert_event_service.record(
            db=db,
            alert_id=alert.alert_id,
            event_type="STATUS_CHANGED",
            old_status=old_status.value,
            new_status=AMLAlertStatus.UNDER_REVIEW.value,
            description=(
                "AML alert moved from OPEN to UNDER_REVIEW "
                "when investigation was created."
            ),
        )

        db.commit()
        db.refresh(updated_alert)

        return investigation

    except ValueError as e:
        raise HTTPException(
            400,
            str(e),
        ) from e

    
@router.post(
    "/aml/investigations/{investigation_id}/run",
)
def run_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    investigation = aml_investigation_service.get(
        db,
        investigation_id,
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    if investigation.status == InvestigationStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail="Completed investigations cannot be re-run",
        )

    
    result = investigation_orchestrator.run(
        db=db,
        alert_id=investigation.alert_id,
        investigation_id=investigation.investigation_id,
    )

    analysis_result = {
        "analysis": result["analysis"].model_dump(mode="json"),
        "assessment": {
            "outcome": result["assessment"].outcome,
            "rationale": result["assessment"].rationale,
            "finding_codes": result["assessment"].finding_codes,
        },
        "recommendation": {
            "action": result["recommendation"].action,
            "rationale": result["recommendation"].rationale,
            "requires_human_approval": result["recommendation"].requires_human_approval,
        },
        "policy_evidence": [
            {
                "policy_id": policy.policy_id,
                "title": policy.title,
                "text": policy.text,
                "relevance_score": policy.relevance_score,
            }
            for policy in result["policy_evidence"]
        ],
        "critic": {
            "passed": result["critic"].passed,
            "issues": result["critic"].issues,
        },
    }

    aml_investigation_service.save_analysis(
        db=db,
        investigation=investigation,
        analysis_result=analysis_result,
    )

    db.commit()
    db.refresh(investigation)

    return {
        "investigation_id": investigation.investigation_id,
        "status": investigation.status.value,
        "analysis_completed_at": investigation.analysis_completed_at,
        "analysis_result": investigation.analysis_result,
    }

@router.get(
    "/aml/investigations",
    response_model=list[AMLInvestigationRead],
)
def list_aml_investigations(
    db: Session = Depends(get_db),
):
    return aml_investigations.list_open(db)

@router.get(
    "/aml/investigations/{investigation_id}",
    response_model=AMLInvestigationRead,
)
def get_aml_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    investigation = aml_investigations.get(
        db,
        investigation_id,
    )

    if not investigation:
        raise HTTPException(
            404,
            "AML investigation not found",
        )

    return investigation

@router.patch(
    "/aml/investigations/{investigation_id}/status",
    response_model=AMLInvestigationRead,
)
def update_aml_investigation_status(
    investigation_id: str,
    request: AMLInvestigationStatusUpdate,
    db: Session = Depends(get_db),
):
    investigation = aml_investigations.get(
        db,
        investigation_id,
    )

    if not investigation:
        raise HTTPException(
            404,
            "AML investigation not found",
        )

    alert = aml_alerts.get(
        db,
        investigation.alert_id,
    )

    if not alert:
        raise HTTPException(
            404,
            "AML alert not found",
        )

    old_status = investigation.status

    try:
        updated = aml_investigation_service.update_status(
            db=db,
            investigation=investigation,
            new_status=request.status,
            conclusion=request.conclusion,
        )
    except ValueError as e:
        raise HTTPException(
            400,
            str(e),
        ) from e

    # Investigation OPEN -> IN_PROGRESS
    # means the investigator has started working the alert.
    if (
        request.status == InvestigationStatus.IN_PROGRESS
        and alert.status == AMLAlertStatus.OPEN
    ):
        aml_alerts.update_status(
            db,
            alert,
            AMLAlertStatus.UNDER_REVIEW,
        )

        aml_alert_event_service.record(
            db=db,
            alert_id=alert.alert_id,
            event_type="STATUS_CHANGED",
            old_status=AMLAlertStatus.OPEN.value,
            new_status=AMLAlertStatus.UNDER_REVIEW.value,
            description=(
                "AML alert moved to UNDER_REVIEW "
                "when investigation started."
            ),
        )

    # Investigation IN_PROGRESS -> COMPLETED
    # means the investigator has finished the case.
    if (
        request.status == InvestigationStatus.COMPLETED
        and alert.status == AMLAlertStatus.UNDER_REVIEW
    ):
        aml_alerts.update_status(
            db,
            alert,
            AMLAlertStatus.CLOSED,
        )

        aml_alert_event_service.record(
            db=db,
            alert_id=alert.alert_id,
            event_type="STATUS_CHANGED",
            old_status=AMLAlertStatus.UNDER_REVIEW.value,
            new_status=AMLAlertStatus.CLOSED.value,
            description=(
                "AML alert closed when investigation "
                "was completed."
            ),
        )

    aml_alert_event_service.record(
        db=db,
        alert_id=investigation.alert_id,
        event_type="INVESTIGATION_STATUS_CHANGED",
        old_status=old_status.value,
        new_status=request.status.value,
        description=(
            f"AML investigation status changed from "
            f"{old_status.value} to {request.status.value}."
        ),
    )

    db.commit()
    db.refresh(updated)

    return updated


@router.get(
    "/aml/investigations/{investigation_id}/case",
    response_model=AMLInvestigationCaseRead,
)

def get_aml_investigation_case(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    investigation = aml_investigations.get(db, investigation_id)

    if not investigation:
        raise HTTPException(404, "AML investigation not found")

    alert = aml_alerts.get(db, investigation.alert_id)

    if not alert:
        raise HTTPException(404, "AML alert not found")

    account = accounts.get(db, alert.account_id)

    if not account:
        raise HTTPException(404, "Account not found")

    aml_profile = db.get(AMLProfile, account.account_id)

    if not aml_profile:
        raise HTTPException(404, "AML profile not found")

    behavior = aml_behavior_service.get_behavior(
        db,
        account.account_id,
    )

    transaction_ids = list(
        db.execute(
            select(AMLAlertTransaction.transaction_id)
            .where(
                AMLAlertTransaction.alert_id == alert.alert_id
            )
        ).scalars()
    )

    transactions = list(
        db.execute(
            select(Transaction)
            .where(
                Transaction.transaction_id.in_(transaction_ids)
            )
            .order_by(Transaction.timestamp.asc())
        ).scalars()
    )

    audit_events = list(
        db.execute(
            select(AMLAlertEvent)
            .where(
                AMLAlertEvent.alert_id == alert.alert_id
            )
            .order_by(AMLAlertEvent.event_time.asc())
        ).scalars()
    )

    findings = evidence_analyzer.analyze(
        alert=alert,
        account=account,
        aml_profile=aml_profile,
        transactions=transactions,
    )
    
    assessment = case_assessment_engine.assess(findings)

    recommendation = recommendation_engine.recommend(assessment)

    # agent_result = investigation_orchestrator.run(
    #     db=db,
    #     alert_id=investigation.alert_id,
    #     investigation_id=investigation.investigation_id,
    # )

    # db.commit()

    agent_executions = agent_execution_service.list_for_investigation(
        db,
        investigation.investigation_id,
    )


    print("\nDEBUG analysis_result:")
    print(investigation.analysis_result)

    return {
        "investigation": investigation,
        "alert": alert,
        "account": account,
        "aml_profile": aml_profile,
        "behavior": behavior,
        "transactions": transactions,
        "audit_events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "old_status": event.old_status,
                "new_status": event.new_status,
                "event_time": event.event_time,
                "description": event.description,
            }
            for event in audit_events
        ],

        "findings": [
            {
                "code": finding.code,
                "severity": finding.severity,
                "title": finding.title,
                "description": finding.description,
                "evidence": finding.evidence,
            }
            
        
            for finding in findings
        ],

        "assessment": {
            "outcome": assessment.outcome,
            "rationale": assessment.rationale,
            "finding_codes": assessment.finding_codes,
        },

        "recommendation": {
            "action": recommendation.action,
            "rationale": recommendation.rationale,
            "requires_human_approval": recommendation.requires_human_approval,
        },
        
        "agent_analysis" : investigation.analysis_result,
        "agent_executions": agent_executions,
    }