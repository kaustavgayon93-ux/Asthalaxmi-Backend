"""
Carbon Credit Assessments & Traceability Router
================================================
NESFIC-D-15: Carbon credit assessment with full traceability to source remote sensing,
field plot measurements, and international registry standards (Verra VCS, Gold Standard).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
import hashlib

from database import get_db
from models import CarbonCreditAssessment, AuditLog
from schemas import CarbonCreditCreate, CarbonCreditResponse

router = APIRouter(prefix="/api/carbon-credits", tags=["Carbon Credits & Traceability"])


@router.get("", response_model=List[CarbonCreditResponse])
def get_carbon_credits(
    division_name: Optional[str] = Query(None),
    standard: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List verified carbon credit assessments with issuance status and audit traceability.
    """
    query = db.query(CarbonCreditAssessment)

    if division_name:
        query = query.filter(CarbonCreditAssessment.division_name == division_name)
    if standard:
        query = query.filter(CarbonCreditAssessment.standard.ilike(f"%{standard}%"))
    if status_filter:
        query = query.filter(CarbonCreditAssessment.status.ilike(f"%{status_filter}%"))

    return query.order_by(desc(CarbonCreditAssessment.created_at)).offset(skip).limit(limit).all()


@router.get("/summary")
def get_carbon_credits_summary(db: Session = Depends(get_db)):
    """
    Returns summary statistics for verified carbon credits across Assam divisions.
    """
    credits = db.query(CarbonCreditAssessment).all()
    total_eligible = sum(c.eligible_credits_tco2e for c in credits)
    total_net_carbon_t = sum(c.net_carbon_change_t for c in credits)
    standards = {}
    statuses = {}
    divisions = {}

    for c in credits:
        standards[c.standard] = standards.get(c.standard, 0) + c.eligible_credits_tco2e
        statuses[c.status] = statuses.get(c.status, 0) + 1
        divisions[c.division_name] = divisions.get(c.division_name, 0) + c.eligible_credits_tco2e

    return {
        "total_assessments": len(credits),
        "total_eligible_credits_tco2e": total_eligible,
        "total_net_carbon_change_t": round(total_net_carbon_t, 2),
        "credits_by_standard": standards,
        "credits_by_status": statuses,
        "credits_by_division": divisions,
    }


@router.get("/{assessment_id}", response_model=CarbonCreditResponse)
def get_carbon_credit(assessment_id: str, db: Session = Depends(get_db)):
    assessment = (
        db.query(CarbonCreditAssessment)
        .filter((CarbonCreditAssessment.id == assessment_id) | (CarbonCreditAssessment.assessment_id == assessment_id))
        .first()
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carbon credit assessment '{assessment_id}' not found",
        )
    return assessment


@router.post("", response_model=CarbonCreditResponse, status_code=status.HTTP_201_CREATED)
def create_carbon_credit(data_in: CarbonCreditCreate, db: Session = Depends(get_db)):
    """
    Issue a new carbon credit assessment with cryptographic SHA-256 seal.
    """
    existing = db.query(CarbonCreditAssessment).filter(
        CarbonCreditAssessment.assessment_id == data_in.assessment_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assessment ID '{data_in.assessment_id}' already registered.",
        )

    # Generate SHA-256 seal for registry integrity
    hash_payload = f"{data_in.assessment_id}:{data_in.division_name}:{data_in.net_carbon_change_t}:{data_in.eligible_credits_tco2e}:{data_in.standard}"
    sha256_seal = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

    credit = CarbonCreditAssessment(
        id=str(uuid.uuid4()),
        sha256_hash=sha256_seal,
        **data_in.model_dump(exclude={"sha256_hash"}),
    )
    db.add(credit)

    log = AuditLog(
        entity_type="CarbonCreditAssessment",
        entity_id=credit.assessment_id,
        action="CREATE",
        changed_by="Assam Forest Carbon Registry Officer",
        description=f"Generated credit assessment {credit.assessment_id} ({credit.eligible_credits_tco2e:,} tCO2e) under {credit.standard}",
    )
    db.add(log)
    db.commit()
    db.refresh(credit)
    return credit
