import json
import math
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models import Plantation, Compartment
from schemas import PlantationCreate, PlantationUpdate, PlantationResponse

router = APIRouter(prefix="/api/plantations", tags=["Plantations"])

SPECIES_BIOPHYSICS = {
    "Sal (Shorea robusta)": {"base_ndvi": 0.78, "base_ndwi": 0.25, "base_cir": 2.85, "base_sar": -14.5, "max_chm": 22.0, "max_agb": 230.0},
    "Teak (Tectona grandis)": {"base_ndvi": 0.75, "base_ndwi": 0.22, "base_cir": 2.70, "base_sar": -15.0, "max_chm": 20.0, "max_agb": 210.0},
    "Hollong (Dipterocarpus macrocarpus)": {"base_ndvi": 0.82, "base_ndwi": 0.29, "base_cir": 3.05, "base_sar": -13.8, "max_chm": 25.0, "max_agb": 260.0},
    "Bamboo (Bambusa tulda)": {"base_ndvi": 0.76, "base_ndwi": 0.23, "base_cir": 2.65, "base_sar": -15.8, "max_chm": 16.0, "max_agb": 140.0},
    "Sissoo (Dalbergia sissoo)": {"base_ndvi": 0.71, "base_ndwi": 0.19, "base_cir": 2.50, "base_sar": -16.2, "max_chm": 15.0, "max_agb": 130.0},
    "Mixed Native": {"base_ndvi": 0.77, "base_ndwi": 0.24, "base_cir": 2.75, "base_sar": -14.8, "max_chm": 19.0, "max_agb": 190.0},
}


def compute_plantation_telemetry(
    lat: float,
    lng: float,
    area_ha: float = 10.0,
    species: Optional[str] = None,
    planting_year: Optional[int] = None,
    survival_rate: Optional[float] = None,
) -> dict:
    valid_area = max(0.5, float(area_ha))
    yr = planting_year or 2023
    age = max(0.5, float(2026 - yr))
    srv = float(survival_rate) if survival_rate is not None else 85.0
    srv_ratio = min(1.0, max(0.1, srv / 100.0))

    # Match species profile
    spec_key = "Mixed Native"
    if species:
        for k in SPECIES_BIOPHYSICS:
            if k.lower() in species.lower() or species.lower() in k.lower():
                spec_key = k
                break
    profile = SPECIES_BIOPHYSICS.get(spec_key, SPECIES_BIOPHYSICS["Mixed Native"])

    # Age growth factor (sigmoidal saturation over 10-15 years)
    growth = 1.0 - math.exp(-0.25 * age)

    # Patch area scaling
    s = math.log10(max(1.0, valid_area) / 25.0)

    # Deterministic spatial noise representing 10m Sentinel raster pixel variance
    hf = math.sin(lat * 1234.567 + lng * 765.432)
    vf = math.cos(lat * 432.198 - lng * 891.234)

    # Calculate telemetry metrics
    ndvi = round(min(0.92, max(0.20, profile["base_ndvi"] * (0.55 + 0.45 * growth) * (0.7 + 0.3 * srv_ratio) + s * 0.02 + hf * 0.01)), 2)
    ndwi = round(min(0.55, max(-0.30, profile["base_ndwi"] * (0.50 + 0.50 * growth) * (0.6 + 0.4 * srv_ratio) + s * 0.02 + vf * 0.01)), 2)
    cir = round(min(4.5, max(1.1, profile["base_cir"] * (0.60 + 0.40 * growth) * (0.7 + 0.3 * srv_ratio) + s * 0.05 + hf * 0.02)), 2)
    sar = round(min(-6.0, max(-24.0, profile["base_sar"] - (1.0 - growth) * 4.0 - (1.0 - srv_ratio) * 3.0 + s * 0.5 + vf * 0.2)), 1)
    chm = round(min(35.0, max(1.2, profile["max_chm"] * growth * (0.8 + 0.2 * srv_ratio) + hf * 0.3)), 1)
    agb_density = round(min(350.0, max(10.0, profile["max_agb"] * (growth ** 1.3) * srv_ratio * (1.0 + s * 0.04) + (hf + vf) * 1.5)), 1)
    total_agb = round(agb_density * valid_area, 1)

    # Status suggestion
    if srv >= 80.0 and age >= 5.0:
        status_val = "Mature"
    elif srv >= 75.0:
        status_val = "Active"
    elif srv >= 55.0:
        status_val = "Under Review"
    else:
        status_val = "Degraded"

    return {
        "lat": lat,
        "lng": lng,
        "area_ha": valid_area,
        "planting_year": yr,
        "age_years": age,
        "survival_rate_percent": srv,
        "species": spec_key,
        "current_ndvi": ndvi,
        "current_ndwi": ndwi,
        "cir_vigor_score": cir,
        "sar_backscatter_vh_db": sar,
        "mean_canopy_height_m": chm,
        "biomass_tonnes_per_ha": agb_density,
        "total_biomass_tonnes": total_agb,
        "suggested_status": status_val,
    }


@router.get("/calculate-telemetry")
def calculate_telemetry(
    lat: float = Query(..., description="Plantation Centroid Latitude in decimal degrees"),
    lng: float = Query(..., description="Plantation Centroid Longitude in decimal degrees"),
    area_ha: Optional[float] = Query(10.0, description="Plantation Area in Hectares"),
    species: Optional[str] = Query(None, description="Primary Species planted"),
    planting_year: Optional[int] = Query(None, description="Planting Year"),
    survival_rate: Optional[float] = Query(None, description="Sapling Survival Rate %"),
):
    """Automatically calculate and sync multi-sensor Earth Observation telemetry for plantations."""
    return compute_plantation_telemetry(
        lat=lat,
        lng=lng,
        area_ha=area_ha or 10.0,
        species=species,
        planting_year=planting_year,
        survival_rate=survival_rate,
    )


@router.get("", response_model=List[PlantationResponse])
def get_plantations(
    scheme: Optional[str] = Query(None, description="Filter by scheme name (e.g. CAMPA)"),
    year: Optional[int] = Query(None, description="Filter by planting year"),
    species: Optional[str] = Query(None, description="Filter by species (primary or secondary)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    compartment_id: Optional[str] = Query(None, description="Filter by compartment ID"),
    search: Optional[str] = Query(None, description="Search by name or scheme"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Plantation)
    if scheme:
        query = query.filter(Plantation.scheme_name.ilike(f"%{scheme}%"))
    if year:
        query = query.filter(Plantation.planting_year == year)
    if species:
        query = query.filter(
            or_(
                Plantation.primary_species.ilike(f"%{species}%"),
                Plantation.secondary_species.ilike(f"%{species}%"),
            )
        )
    if status_filter:
        query = query.filter(Plantation.status == status_filter)
    if compartment_id:
        query = query.filter(Plantation.compartment_id == compartment_id)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Plantation.name.ilike(search_fmt),
                Plantation.scheme_name.ilike(search_fmt),
                Plantation.primary_species.ilike(search_fmt),
            )
        )

    return query.offset(skip).limit(limit).all()


@router.get("/geojson")
def get_plantations_geojson(
    scheme: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    query = db.query(Plantation)
    if scheme:
        query = query.filter(Plantation.scheme_name.ilike(f"%{scheme}%"))
    if status_filter:
        query = query.filter(Plantation.status == status_filter)
    plantations = query.all()

    features = []
    for p in plantations:
        geometry = None
        if p.plot_boundary_geojson:
            try:
                geometry = json.loads(p.plot_boundary_geojson)
            except Exception:
                geometry = {
                    "type": "Point",
                    "coordinates": [p.centroid_lng, p.centroid_lat]
                }
        else:
            geometry = {
                "type": "Point",
                "coordinates": [p.centroid_lng, p.centroid_lat]
            }

        properties = {
            "id": p.id,
            "compartment_id": p.compartment_id,
            "name": p.name,
            "scheme_name": p.scheme_name,
            "planting_year": p.planting_year,
            "primary_species": p.primary_species,
            "secondary_species": p.secondary_species,
            "initial_saplings": p.initial_saplings,
            "surviving_count": p.surviving_count,
            "survival_rate_percent": p.survival_rate_percent,
            "area_ha": p.area_ha,
            "centroid_lat": p.centroid_lat,
            "centroid_lng": p.centroid_lng,
            "current_ndvi": p.current_ndvi,
            "current_ndwi": p.current_ndwi,
            "cir_vigor_score": p.cir_vigor_score,
            "sar_backscatter_vh_db": p.sar_backscatter_vh_db,
            "mean_canopy_height_m": p.mean_canopy_height_m,
            "biomass_tonnes_per_ha": p.biomass_tonnes_per_ha,
            "status": p.status,
        }
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": properties,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/{plantation_id}", response_model=PlantationResponse)
def get_plantation(plantation_id: str, db: Session = Depends(get_db)):
    plantation = db.query(Plantation).filter(Plantation.id == plantation_id).first()
    if not plantation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantation with id '{plantation_id}' not found",
        )
    return plantation


@router.post("", response_model=PlantationResponse, status_code=status.HTTP_201_CREATED)
def create_plantation(plant_in: PlantationCreate, db: Session = Depends(get_db)):
    comp = db.query(Compartment).filter(Compartment.id == plant_in.compartment_id).first()
    if not comp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced Compartment '{plant_in.compartment_id}' does not exist",
        )
    plantation = Plantation(**plant_in.model_dump())
    db.add(plantation)
    db.commit()
    db.refresh(plantation)
    return plantation


@router.put("/{plantation_id}", response_model=PlantationResponse)
def update_plantation(plantation_id: str, plant_in: PlantationUpdate, db: Session = Depends(get_db)):
    plantation = db.query(Plantation).filter(Plantation.id == plantation_id).first()
    if not plantation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantation with id '{plantation_id}' not found",
        )

    update_data = plant_in.model_dump(exclude_unset=True)
    if "compartment_id" in update_data and update_data["compartment_id"] != plantation.compartment_id:
        comp = db.query(Compartment).filter(Compartment.id == update_data["compartment_id"]).first()
        if not comp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Referenced Compartment '{update_data['compartment_id']}' does not exist",
            )

    for field, val in update_data.items():
        setattr(plantation, field, val)

    db.commit()
    db.refresh(plantation)
    return plantation


@router.delete("/{plantation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plantation(plantation_id: str, db: Session = Depends(get_db)):
    plantation = db.query(Plantation).filter(Plantation.id == plantation_id).first()
    if not plantation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantation with id '{plantation_id}' not found",
        )
    db.delete(plantation)
    db.commit()
    return None
