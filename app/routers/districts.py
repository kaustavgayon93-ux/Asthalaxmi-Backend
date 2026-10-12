from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import District, DistrictUpdate
from app.services.data_manager import data_manager

router = APIRouter(prefix="/districts", tags=["Districts"])

@router.get("", response_model=List[District], summary="List all 35 administrative districts in Assam")
def get_all_districts():
    return data_manager.get_districts()

@router.get("/{district_id}", response_model=District, summary="Get details for a specific district")
def get_district_by_id(district_id: str):
    dist = data_manager.get_district(district_id)
    if not dist:
        raise HTTPException(status_code=404, detail=f"District '{district_id}' not found.")
    return dist

@router.put("/{district_id}", response_model=District, summary="Update district acreage, yield, flood, or uncertainty metrics")
def update_district(district_id: str, dist_in: DistrictUpdate):
    updated = data_manager.update_district(district_id, dist_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"District '{district_id}' not found.")
    return updated
