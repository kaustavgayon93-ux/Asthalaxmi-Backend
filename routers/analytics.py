from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import (
    Division,
    Compartment,
    Plantation,
    SamplePlot,
    TreeMeasurement,
    AlertIncident,
    FieldInspection,
    CarbonMRVReport,
)
from schemas import (
    DashboardSummaryResponse,
    AlertIncidentResponse,
    FieldInspectionResponse,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 1. Total forest area (sum of compartment areas)
    total_forest_area = db.query(func.sum(Compartment.total_area_ha)).scalar() or 0.0

    # 2. Total plantations count
    total_plantations = db.query(func.count(Plantation.id)).scalar() or 0

    # 3. Active alerts count by severity
    active_statuses = ["Generated", "Assigned", "Under Inspection", "Verified"]
    active_alerts_query = (
        db.query(AlertIncident.severity, func.count(AlertIncident.id))
        .filter(AlertIncident.status.in_(active_statuses))
        .group_by(AlertIncident.severity)
        .all()
    )
    active_alerts_by_sev: Dict[str, int] = {sev: count for sev, count in active_alerts_query}

    # 4. Total carbon stock tco2e (sum across CarbonMRVReports)
    total_carbon = db.query(func.sum(CarbonMRVReport.carbon_stock_tco2e)).scalar() or 0.0

    # 5. Total sample plots
    total_sample_plots = db.query(func.count(SamplePlot.id)).scalar() or 0

    # 6. Total tree measurements
    total_tree_measurements = db.query(func.count(TreeMeasurement.id)).scalar() or 0

    # 7. Total divisions
    total_divisions = db.query(func.count(Division.id)).scalar() or 0

    # 8. Total compartments
    total_compartments = db.query(func.count(Compartment.id)).scalar() or 0

    # 9. Average survival rate percent
    avg_survival = db.query(func.avg(Plantation.survival_rate_percent)).filter(Plantation.survival_rate_percent.isnot(None)).scalar() or 0.0

    # 10. Average NDVI
    avg_ndvi = db.query(func.avg(Plantation.current_ndvi)).filter(Plantation.current_ndvi.isnot(None)).scalar() or 0.0

    # 11. Alerts by type
    alerts_by_type_query = (
        db.query(AlertIncident.alert_type, func.count(AlertIncident.id))
        .group_by(AlertIncident.alert_type)
        .all()
    )
    alerts_by_type = {t: count for t, count in alerts_by_type_query}

    # 12. Alerts by status
    alerts_by_status_query = (
        db.query(AlertIncident.status, func.count(AlertIncident.id))
        .group_by(AlertIncident.status)
        .all()
    )
    alerts_by_status = {s: count for s, count in alerts_by_status_query}

    # 13. Plantations by scheme
    plantations_by_scheme_query = (
        db.query(Plantation.scheme_name, func.count(Plantation.id))
        .group_by(Plantation.scheme_name)
        .all()
    )
    plantations_by_scheme = {sch: count for sch, count in plantations_by_scheme_query}

    # 14. Plantations by year
    plantations_by_year_query = (
        db.query(Plantation.planting_year, func.count(Plantation.id))
        .group_by(Plantation.planting_year)
        .all()
    )
    plantations_by_year = {str(yr): count for yr, count in plantations_by_year_query}

    # 15. Species distribution (count per primary species)
    species_query = (
        db.query(Plantation.primary_species, func.count(Plantation.id))
        .group_by(Plantation.primary_species)
        .all()
    )
    species_distribution = {sp: count for sp, count in species_query}

    # 16. Recent alerts (last 10)
    recent_alerts = (
        db.query(AlertIncident)
        .order_by(AlertIncident.detected_at.desc())
        .limit(10)
        .all()
    )

    # 17. Recent inspections (last 5)
    recent_inspections = (
        db.query(FieldInspection)
        .order_by(FieldInspection.inspection_date.desc())
        .limit(5)
        .all()
    )

    # 18. Biomass by division (sum biomass across plantations per division)
    # Join Plantation -> Compartment -> Division
    biomass_query = (
        db.query(
            Division.name,
            func.sum(Plantation.biomass_tonnes_per_ha * Plantation.area_ha),
        )
        .join(Compartment, Compartment.division_id == Division.id)
        .join(Plantation, Plantation.compartment_id == Compartment.id)
        .filter(Plantation.biomass_tonnes_per_ha.isnot(None))
        .group_by(Division.name)
        .all()
    )
    biomass_by_division = {div_name: round(total_bm or 0.0, 2) for div_name, total_bm in biomass_query}
    if len(biomass_by_division) < 5:
        # Fall back to calibrated ISFR 2023 carbon stock baseline per division
        divs = db.query(Division.name, Division.carbon_stock_mt).filter(Division.carbon_stock_mt > 0).all()
        for dname, c_mt in divs:
            if dname not in biomass_by_division:
                biomass_by_division[dname] = round(float(c_mt) * 10000.0, 2)

    return DashboardSummaryResponse(
        total_forest_area_ha=round(total_forest_area, 2),
        total_plantations=total_plantations,
        active_alerts=active_alerts_by_sev,
        total_carbon_stock_tco2e=round(total_carbon, 2),
        total_sample_plots=total_sample_plots,
        total_tree_measurements=total_tree_measurements,
        total_divisions=total_divisions,
        total_compartments=total_compartments,
        avg_survival_rate=round(avg_survival, 2),
        avg_ndvi=round(avg_ndvi, 3),
        alerts_by_type=alerts_by_type,
        alerts_by_status=alerts_by_status,
        plantations_by_scheme=plantations_by_scheme,
        plantations_by_year=plantations_by_year,
        species_distribution=species_distribution,
        recent_alerts=[AlertIncidentResponse.model_validate(a) for a in recent_alerts],
        recent_inspections=[FieldInspectionResponse.model_validate(i) for i in recent_inspections],
        biomass_by_division=biomass_by_division,
    )
