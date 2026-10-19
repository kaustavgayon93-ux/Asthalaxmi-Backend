from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import AuditLog
from schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit-log", tags=["Audit Log"])


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Plantation, AlertIncident, etc.)"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, UPDATE, DELETE, etc.)"),
    start_date: Optional[datetime] = Query(None, description="Filter logs starting at this timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter logs ending at this timestamp"),
    search: Optional[str] = Query(None, description="Search description or changed_by"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                AuditLog.description.ilike(search_fmt),
                AuditLog.changed_by.ilike(search_fmt),
                AuditLog.entity_id.ilike(search_fmt),
            )
        )

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(log_id: str, db: Session = Depends(get_db)):
    log_entry = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AuditLog with id '{log_id}' not found",
        )
    return log_entry
