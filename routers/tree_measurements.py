from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from database import get_db
from models import TreeMeasurement, SamplePlot
from schemas import TreeMeasurementCreate, TreeMeasurementUpdate, TreeMeasurementResponse

router = APIRouter(prefix="/api/tree-measurements", tags=["Tree Measurements"])


@router.get("", response_model=List[TreeMeasurementResponse])
def get_tree_measurements(
    sample_plot_id: Optional[str] = Query(None, description="Filter by sample plot ID or plot code"),
    species: Optional[str] = Query(None, description="Filter by species code, local name, or botanical name"),
    health_status: Optional[str] = Query(None, description="Filter by health status"),
    search: Optional[str] = Query(None, description="Search by species or notes"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(TreeMeasurement).options(joinedload(TreeMeasurement.sample_plot))
    if sample_plot_id:
        query = query.join(TreeMeasurement.sample_plot).filter(
            or_(TreeMeasurement.sample_plot_id == sample_plot_id, SamplePlot.plot_code == sample_plot_id)
        )
    if species:
        species_fmt = f"%{species}%"
        query = query.filter(
            or_(
                TreeMeasurement.species_code.ilike(species_fmt),
                TreeMeasurement.species_local_name.ilike(species_fmt),
                TreeMeasurement.species_botanical_name.ilike(species_fmt),
            )
        )
    if health_status:
        query = query.filter(TreeMeasurement.health_status == health_status)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                TreeMeasurement.species_local_name.ilike(search_fmt),
                TreeMeasurement.species_botanical_name.ilike(search_fmt),
                TreeMeasurement.notes.ilike(search_fmt),
            )
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{measurement_id}", response_model=TreeMeasurementResponse)
def get_tree_measurement(measurement_id: str, db: Session = Depends(get_db)):
    tm = db.query(TreeMeasurement).options(joinedload(TreeMeasurement.sample_plot)).filter(TreeMeasurement.id == measurement_id).first()
    if not tm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TreeMeasurement with id '{measurement_id}' not found",
        )
    return tm


@router.post("", response_model=TreeMeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_tree_measurement(tm_in: TreeMeasurementCreate, db: Session = Depends(get_db)):
    sp = db.query(SamplePlot).filter(
        or_(SamplePlot.id == tm_in.sample_plot_id, SamplePlot.plot_code == tm_in.sample_plot_id)
    ).first()
    if not sp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced SamplePlot '{tm_in.sample_plot_id}' does not exist. Plot code must be selected from registered sample plots only.",
        )

    data = tm_in.model_dump()
    data["sample_plot_id"] = sp.id
    # Compute dbh_cm from gbh_cm if not provided
    if data.get("dbh_cm") is None and data.get("gbh_cm") is not None:
        data["dbh_cm"] = round(data["gbh_cm"] / 3.14159, 2)

    tm = TreeMeasurement(**data)
    db.add(tm)
    db.commit()
    db.refresh(tm)
    return tm


@router.put("/{measurement_id}", response_model=TreeMeasurementResponse)
def update_tree_measurement(
    measurement_id: str,
    tm_in: TreeMeasurementUpdate,
    db: Session = Depends(get_db),
):
    tm = db.query(TreeMeasurement).options(joinedload(TreeMeasurement.sample_plot)).filter(TreeMeasurement.id == measurement_id).first()
    if not tm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TreeMeasurement with id '{measurement_id}' not found",
        )

    update_data = tm_in.model_dump(exclude_unset=True)
    if "sample_plot_id" in update_data and update_data["sample_plot_id"]:
        sp = db.query(SamplePlot).filter(
            or_(SamplePlot.id == update_data["sample_plot_id"], SamplePlot.plot_code == update_data["sample_plot_id"])
        ).first()
        if not sp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Referenced SamplePlot '{update_data['sample_plot_id']}' does not exist. Plot code must be selected from registered sample plots only.",
            )
        update_data["sample_plot_id"] = sp.id

    if "gbh_cm" in update_data and "dbh_cm" not in update_data:
        update_data["dbh_cm"] = round(update_data["gbh_cm"] / 3.14159, 2)

    for field, val in update_data.items():
        setattr(tm, field, val)

    db.commit()
    db.refresh(tm)
    return tm


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tree_measurement(measurement_id: str, db: Session = Depends(get_db)):
    tm = db.query(TreeMeasurement).filter(TreeMeasurement.id == measurement_id).first()
    if not tm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TreeMeasurement with id '{measurement_id}' not found",
        )
    db.delete(tm)
    db.commit()
    return None
