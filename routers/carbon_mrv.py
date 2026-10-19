import hashlib
import json
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import CarbonMRVReport, Compartment, Plantation, AuditLog
from schemas import (
    CarbonMRVReportCreate,
    CarbonMRVReportUpdate,
    CarbonMRVReportResponse,
)

router = APIRouter(prefix="/api/carbon-reports", tags=["Carbon MRV"])


@router.get("", response_model=List[CarbonMRVReportResponse])
def get_carbon_reports(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by report status"),
    report_type: Optional[str] = Query(None, alias="type", description="Filter by report type (Baseline, Monitoring, Verification)"),
    compartment_id: Optional[str] = Query(None, description="Filter by compartment ID"),
    plantation_id: Optional[str] = Query(None, description="Filter by plantation ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(CarbonMRVReport)
    if status_filter:
        query = query.filter(CarbonMRVReport.status == status_filter)
    if report_type:
        query = query.filter(CarbonMRVReport.report_type == report_type)
    if compartment_id:
        query = query.filter(CarbonMRVReport.compartment_id == compartment_id)
    if plantation_id:
        query = query.filter(CarbonMRVReport.plantation_id == plantation_id)

    return query.order_by(CarbonMRVReport.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=CarbonMRVReportResponse)
def get_carbon_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(CarbonMRVReport).filter(CarbonMRVReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CarbonMRVReport with id '{report_id}' not found",
        )
    return report


@router.post("", response_model=CarbonMRVReportResponse, status_code=status.HTTP_201_CREATED)
def create_carbon_report(report_in: CarbonMRVReportCreate, db: Session = Depends(get_db)):
    if report_in.compartment_id:
        comp = db.query(Compartment).filter(Compartment.id == report_in.compartment_id).first()
        if not comp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Referenced Compartment '{report_in.compartment_id}' does not exist",
            )
    if report_in.plantation_id:
        plant = db.query(Plantation).filter(Plantation.id == report_in.plantation_id).first()
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Referenced Plantation '{report_in.plantation_id}' does not exist",
            )

    report = CarbonMRVReport(**report_in.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.put("/{report_id}", response_model=CarbonMRVReportResponse)
def update_carbon_report(
    report_id: str,
    report_in: CarbonMRVReportUpdate,
    db: Session = Depends(get_db),
):
    report = db.query(CarbonMRVReport).filter(CarbonMRVReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CarbonMRVReport with id '{report_id}' not found",
        )

    update_data = report_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(report, field, val)

    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_carbon_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(CarbonMRVReport).filter(CarbonMRVReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CarbonMRVReport with id '{report_id}' not found",
        )
    db.delete(report)
    db.commit()
    return None


class IPCCCalculationRequest(BaseModel):
    total_agb_tonnes: float
    area_ha: Optional[float] = None
    uncertainty_percent: Optional[float] = 6.5
    root_to_shoot_ratio: Optional[float] = 0.26
    carbon_fraction: Optional[float] = 0.47


class IPCCCalculationResponse(BaseModel):
    agb_tonnes: float
    root_to_shoot_ratio: float
    bgb_tonnes: float
    total_biomass_tonnes: float
    carbon_fraction: float
    carbon_stock_tc: float
    co2_molecular_ratio: float
    tco2e_carbon_credits: float
    agb_per_ha: Optional[float] = None
    carbon_density_tc_ha: Optional[float] = None
    uncertainty_percent: float
    ci_lower_tco2e: float
    ci_upper_tco2e: float
    methodology: str
    sha256_hash: str
    timestamp: str


@router.post("/calculate-ipcc", response_model=IPCCCalculationResponse)
def calculate_ipcc_carbon(req: IPCCCalculationRequest):
    """
    Executes the 5-step IPCC 2006 GL Vol-4 AFOLU Tier-2 Carbon Equation:
    1. AGB: Above-ground biomass (tonnes)
    2. BGB: Below-ground biomass = AGB * 0.26 (Root-to-shoot ratio R=0.26)
    3. Total Biomass = AGB + BGB
    4. Carbon Stock (tC) = Total Biomass * 0.47 (Carbon Fraction CF=0.47)
    5. Carbon Credits (tCO2e) = Carbon Stock * (44/12) = Carbon Stock * 3.67
    Computes 95% Confidence Interval and SHA-256 integrity seal.
    """
    r = req.root_to_shoot_ratio if req.root_to_shoot_ratio is not None else 0.26
    cf = req.carbon_fraction if req.carbon_fraction is not None else 0.47
    uncert = req.uncertainty_percent if req.uncertainty_percent is not None else 6.5

    agb = req.total_agb_tonnes
    bgb = round(agb * r, 2)
    total_biomass = round(agb + bgb, 2)
    c_stock = round(total_biomass * cf, 2)
    molecular_ratio = 3.67  # 44/12
    tco2e = round(c_stock * molecular_ratio, 2)

    agb_per_ha = round(agb / req.area_ha, 2) if req.area_ha and req.area_ha > 0 else None
    c_density = round(c_stock / req.area_ha, 2) if req.area_ha and req.area_ha > 0 else None

    ci_lower = round(tco2e * (1.0 - (uncert / 100.0)), 2)
    ci_upper = round(tco2e * (1.0 + (uncert / 100.0)), 2)

    now_iso = datetime.now(timezone.utc).isoformat()
    raw_signature = f"IPCC_2006_AFOLU:{agb}:{bgb}:{total_biomass}:{c_stock}:{tco2e}:{now_iso}"
    sha256 = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

    return IPCCCalculationResponse(
        agb_tonnes=agb,
        root_to_shoot_ratio=r,
        bgb_tonnes=bgb,
        total_biomass_tonnes=total_biomass,
        carbon_fraction=cf,
        carbon_stock_tc=c_stock,
        co2_molecular_ratio=molecular_ratio,
        tco2e_carbon_credits=tco2e,
        agb_per_ha=agb_per_ha,
        carbon_density_tc_ha=c_density,
        uncertainty_percent=uncert,
        ci_lower_tco2e=ci_lower,
        ci_upper_tco2e=ci_upper,
        methodology="IPCC 2006 Guidelines for National GHG Inventories - Vol 4 AFOLU (Tier-2)",
        sha256_hash=sha256,
        timestamp=now_iso,
    )

