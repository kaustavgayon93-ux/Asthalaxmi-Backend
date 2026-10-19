from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import FieldInspection, AlertIncident, User
from schemas import (
    FieldInspectionCreate,
    FieldInspectionUpdate,
    FieldInspectionResponse,
)

router = APIRouter(prefix="/api/field-inspections", tags=["Field Inspections"])


@router.get("", response_model=List[FieldInspectionResponse])
def get_field_inspections(
    alert_id: Optional[str] = Query(None, description="Filter by alert ID"),
    officer_id: Optional[str] = Query(None, description="Filter by officer user ID"),
    cause: Optional[str] = Query(None, description="Filter by cause"),
    search: Optional[str] = Query(None, description="Search remarks or action taken"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(FieldInspection)
    if alert_id:
        query = query.filter(FieldInspection.alert_id == alert_id)
    if officer_id:
        query = query.filter(FieldInspection.officer_id == officer_id)
    if cause:
        query = query.filter(FieldInspection.cause == cause)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                FieldInspection.remarks.ilike(search_fmt),
                FieldInspection.action_taken.ilike(search_fmt),
            )
        )

    return query.order_by(FieldInspection.inspection_date.desc()).offset(skip).limit(limit).all()


@router.get("/{inspection_id}", response_model=FieldInspectionResponse)
def get_field_inspection(inspection_id: str, db: Session = Depends(get_db)):
    inspection = db.query(FieldInspection).filter(FieldInspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldInspection with id '{inspection_id}' not found",
        )
    return inspection


@router.post("", response_model=FieldInspectionResponse, status_code=status.HTTP_201_CREATED)
def create_field_inspection(insp_in: FieldInspectionCreate, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == insp_in.alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced Alert '{insp_in.alert_id}' does not exist",
        )
    officer = db.query(User).filter(User.id == insp_in.officer_id).first()
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced Officer '{insp_in.officer_id}' does not exist",
        )

    data = insp_in.model_dump()
    if not data.get("inspection_date"):
        data["inspection_date"] = datetime.now(timezone.utc)
    if not data.get("synced_at"):
        data["synced_at"] = datetime.now(timezone.utc)

    insp = FieldInspection(**data)
    db.add(insp)

    # Automatically transition alert to Verified or False Alert if appropriate
    if insp.cause == "False Alert":
        alert.status = "False Alert"
        alert.resolved_at = datetime.now(timezone.utc)
    elif alert.status in ["Generated", "Assigned", "Under Inspection"]:
        alert.status = "Verified"

    db.commit()
    db.refresh(insp)
    return insp


@router.put("/{inspection_id}", response_model=FieldInspectionResponse)
def update_field_inspection(
    inspection_id: str,
    insp_in: FieldInspectionUpdate,
    db: Session = Depends(get_db),
):
    insp = db.query(FieldInspection).filter(FieldInspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldInspection with id '{inspection_id}' not found",
        )

    update_data = insp_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(insp, field, val)

    db.commit()
    db.refresh(insp)
    return insp


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_inspection(inspection_id: str, db: Session = Depends(get_db)):
    insp = db.query(FieldInspection).filter(FieldInspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FieldInspection with id '{inspection_id}' not found",
        )
    db.delete(insp)
    db.commit()
    return None
