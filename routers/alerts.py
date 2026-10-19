from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import AlertIncident, Compartment, User
from schemas import (
    AlertIncidentCreate,
    AlertIncidentUpdate,
    AlertIncidentResponse,
    AlertStatusUpdate,
    AlertAssignUpdate,
)

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertIncidentResponse])
def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by alert status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    start_date: Optional[datetime] = Query(None, description="Start date for detected_at"),
    end_date: Optional[datetime] = Query(None, description="End date for detected_at"),
    compartment_id: Optional[str] = Query(None, description="Filter by compartment ID"),
    search: Optional[str] = Query(None, description="Search description or satellite scene"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(AlertIncident)
    if status_filter:
        query = query.filter(AlertIncident.status == status_filter)
    if severity:
        query = query.filter(AlertIncident.severity == severity)
    if alert_type:
        query = query.filter(AlertIncident.alert_type == alert_type)
    if start_date:
        query = query.filter(AlertIncident.detected_at >= start_date)
    if end_date:
        query = query.filter(AlertIncident.detected_at <= end_date)
    if compartment_id:
        query = query.filter(AlertIncident.compartment_id == compartment_id)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                AlertIncident.description.ilike(search_fmt),
                AlertIncident.satellite_scene_id.ilike(search_fmt),
            )
        )

    return query.order_by(AlertIncident.detected_at.desc()).offset(skip).limit(limit).all()


@router.get("/geojson")
def get_alerts_geojson(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    query = db.query(AlertIncident)
    if status_filter:
        query = query.filter(AlertIncident.status == status_filter)
    if severity:
        query = query.filter(AlertIncident.severity == severity)
    if alert_type:
        query = query.filter(AlertIncident.alert_type == alert_type)
    alerts = query.all()

    features = []
    for a in alerts:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [a.centroid_lng, a.centroid_lat],
            },
            "properties": {
                "id": a.id,
                "compartment_id": a.compartment_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "affected_area_ha": a.affected_area_ha,
                "confidence_score": a.confidence_score,
                "status": a.status,
                "assigned_to": a.assigned_to,
                "description": a.description,
                "detected_at": a.detected_at.isoformat() if a.detected_at else None,
                "satellite_scene_id": a.satellite_scene_id,
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/{alert_id}", response_model=AlertIncidentResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )
    return alert


@router.post("", response_model=AlertIncidentResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertIncidentCreate, db: Session = Depends(get_db)):
    comp = db.query(Compartment).filter(Compartment.id == alert_in.compartment_id).first()
    if not comp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced Compartment '{alert_in.compartment_id}' does not exist",
        )
    data = alert_in.model_dump()
    if not data.get("detected_at"):
        data["detected_at"] = datetime.now(timezone.utc)

    alert = AlertIncident(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}", response_model=AlertIncidentResponse)
def update_alert(alert_id: str, alert_in: AlertIncidentUpdate, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )

    update_data = alert_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(alert, field, val)

    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/status", response_model=AlertIncidentResponse)
def update_alert_status(alert_id: str, status_in: AlertStatusUpdate, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )

    alert.status = status_in.status
    if status_in.status in ["Closed", "Action Taken", "False Alert"]:
        alert.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/assign", response_model=AlertIncidentResponse)
def assign_alert(alert_id: str, assign_in: AlertAssignUpdate, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )

    user = db.query(User).filter(User.id == assign_in.assigned_to).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assignee User '{assign_in.assigned_to}' not found",
        )

    alert.assigned_to = assign_in.assigned_to
    if assign_in.assigned_by:
        alert.assigned_by = assign_in.assigned_by
    alert.assigned_at = datetime.now(timezone.utc)
    if alert.status == "Generated":
        alert.status = "Assigned"

    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(AlertIncident).filter(AlertIncident.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )
    db.delete(alert)
    db.commit()
    return None
