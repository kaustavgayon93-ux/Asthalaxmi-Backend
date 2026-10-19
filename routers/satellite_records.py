"""
Optical & SAR Satellite Remote Sensing Router
==============================================
NESFIC-D-15: Optical/SAR remote sensing fusion for persistent forest & plantation monitoring,
addressing 60-85% monsoon cloud occlusion in Assam via Sentinel-1 C-band & RISAT-2B radar.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from database import get_db
from models import SatelliteScene, AuditLog
from schemas import SatelliteRecordCreate, SatelliteRecordResponse, SatelliteRecordUpdate

router = APIRouter(prefix="/api/satellite-records", tags=["Satellite Remote Sensing"])


@router.get("", response_model=List[SatelliteRecordResponse])
def get_satellite_records(
    sensor_type: Optional[str] = Query(None, description="optical, sar, or all"),
    division_name: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List satellite scenes and temporal monitoring records with Optical & SAR radar backscatter.
    Supports filtering by sensor type ('sar', 'optical', or specific satellite).
    """
    query = db.query(SatelliteScene)

    if sensor_type:
        st = sensor_type.lower()
        if st == "sar":
            query = query.filter(
                (SatelliteScene.sensor_type.ilike("%sar%")) |
                (SatelliteScene.satellite_name.ilike("%sentinel-1%")) |
                (SatelliteScene.satellite_name.ilike("%risat%")) |
                (SatelliteScene.satellite_name.ilike("%eos-04%"))
            )
        elif st == "optical":
            query = query.filter(
                ~SatelliteScene.sensor_type.ilike("%sar%"),
                ~SatelliteScene.satellite_name.ilike("%sentinel-1%"),
                ~SatelliteScene.satellite_name.ilike("%risat%"),
            )

    if division_name and division_name != "All Divisions":
        query = query.filter(SatelliteScene.division_name == division_name)

    return query.order_by(desc(SatelliteScene.acquisition_date)).offset(skip).limit(limit).all()


@router.get("/{scene_id}", response_model=SatelliteRecordResponse)
def get_satellite_record(scene_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(SatelliteScene)
        .filter((SatelliteScene.id == scene_id) | (SatelliteScene.scene_id == scene_id))
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite record '{scene_id}' not found",
        )
    return record


@router.post("", response_model=SatelliteRecordResponse, status_code=status.HTTP_201_CREATED)
def create_satellite_record(record_in: SatelliteRecordCreate, db: Session = Depends(get_db)):
    """
    Ingest a new optical or SAR radar remote sensing acquisition record.
    """
    existing = db.query(SatelliteScene).filter(SatelliteScene.scene_id == record_in.scene_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Satellite scene with ID '{record_in.scene_id}' already exists.",
        )

    scene = SatelliteScene(
        id=str(uuid.uuid4()),
        **record_in.model_dump(),
    )
    db.add(scene)

    log = AuditLog(
        entity_type="SatelliteScene",
        entity_id=scene.scene_id,
        action="CREATE",
        changed_by="ASSAC Remote Sensing Data Pipeline",
        description=f"Ingested satellite scene {scene.scene_id} ({scene.satellite_name}) for {scene.division_name}",
    )
    db.add(log)
    db.commit()
    db.refresh(scene)
    return scene


@router.put("/{id}", response_model=SatelliteRecordResponse)
def update_satellite_record(id: str, record_in: SatelliteRecordUpdate, db: Session = Depends(get_db)):
    scene = db.query(SatelliteScene).filter((SatelliteScene.id == id) | (SatelliteScene.scene_id == id)).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Satellite scene not found")

    update_data = record_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(scene, field, val)

    audit = AuditLog(
        id=str(uuid.uuid4()),
        entity_type="SatelliteScene",
        entity_id=scene.id,
        action="UPDATE",
        changed_by="ASSAC Operator",
        description=f"Updated satellite scene {scene.scene_id}",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit)
    db.commit()
    db.refresh(scene)
    return scene


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_satellite_record(id: str, db: Session = Depends(get_db)):
    scene = db.query(SatelliteScene).filter((SatelliteScene.id == id) | (SatelliteScene.scene_id == id)).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Satellite scene not found")

    db.delete(scene)
    audit = AuditLog(
        id=str(uuid.uuid4()),
        entity_type="SatelliteScene",
        entity_id=id,
        action="DELETE",
        changed_by="ASSAC Operator",
        description=f"Deleted satellite scene {scene.scene_id}",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(audit)
    db.commit()
    return None
