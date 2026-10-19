from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import SamplePlot, Plantation
from schemas import SamplePlotCreate, SamplePlotUpdate, SamplePlotResponse

router = APIRouter(prefix="/api/sample-plots", tags=["Sample Plots"])


@router.get("", response_model=List[SamplePlotResponse])
def get_sample_plots(
    plantation_id: Optional[str] = Query(None, description="Filter by plantation ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by plot code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(SamplePlot)
    if plantation_id:
        query = query.filter(SamplePlot.plantation_id == plantation_id)
    if status_filter:
        query = query.filter(SamplePlot.status == status_filter)
    if search:
        query = query.filter(SamplePlot.plot_code.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{plot_id}", response_model=SamplePlotResponse)
def get_sample_plot(plot_id: str, db: Session = Depends(get_db)):
    plot = db.query(SamplePlot).filter(SamplePlot.id == plot_id).first()
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SamplePlot with id '{plot_id}' not found",
        )
    return plot


@router.post("", response_model=SamplePlotResponse, status_code=status.HTTP_201_CREATED)
def create_sample_plot(plot_in: SamplePlotCreate, db: Session = Depends(get_db)):
    plant = db.query(Plantation).filter(Plantation.id == plot_in.plantation_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced Plantation '{plot_in.plantation_id}' does not exist",
        )
    existing = db.query(SamplePlot).filter(SamplePlot.plot_code == plot_in.plot_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SamplePlot with plot_code '{plot_in.plot_code}' already exists",
        )

    plot = SamplePlot(**plot_in.model_dump())
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot


@router.put("/{plot_id}", response_model=SamplePlotResponse)
def update_sample_plot(plot_id: str, plot_in: SamplePlotUpdate, db: Session = Depends(get_db)):
    plot = db.query(SamplePlot).filter(SamplePlot.id == plot_id).first()
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SamplePlot with id '{plot_id}' not found",
        )

    update_data = plot_in.model_dump(exclude_unset=True)
    if "plot_code" in update_data and update_data["plot_code"] != plot.plot_code:
        existing = db.query(SamplePlot).filter(SamplePlot.plot_code == update_data["plot_code"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SamplePlot with plot_code '{update_data['plot_code']}' already exists",
            )

    for field, val in update_data.items():
        setattr(plot, field, val)

    db.commit()
    db.refresh(plot)
    return plot


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample_plot(plot_id: str, db: Session = Depends(get_db)):
    plot = db.query(SamplePlot).filter(SamplePlot.id == plot_id).first()
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SamplePlot with id '{plot_id}' not found",
        )
    db.delete(plot)
    db.commit()
    return None
