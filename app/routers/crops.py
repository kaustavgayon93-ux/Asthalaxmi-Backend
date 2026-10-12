from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import Crop, CropCreate, CropUpdate
from app.services.data_manager import data_manager

router = APIRouter(prefix="/crops", tags=["Crops"])

@router.get("", response_model=List[Crop], summary="List all crops grown in Assam")
def get_all_crops(
    category: Optional[str] = Query(None, description="Filter by crop category (e.g. 'Cereals & Grains', 'Oilseeds', etc.)")
):
    return data_manager.get_crops(category=category)

@router.get("/{crop_id}", response_model=Crop, summary="Get details for a specific crop")
def get_crop_by_id(crop_id: str):
    crop = data_manager.get_crop(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop with ID '{crop_id}' not found.")
    return crop

@router.post("", response_model=Crop, status_code=201, summary="Add a new crop to the master database")
def create_crop(crop_in: CropCreate):
    if data_manager.get_crop(crop_in.id):
        raise HTTPException(status_code=400, detail=f"Crop with ID '{crop_in.id}' already exists.")
    return data_manager.create_crop(crop_in)

@router.put("/{crop_id}", response_model=Crop, summary="Update crop baseline parameters")
def update_crop(crop_id: str, crop_in: CropUpdate):
    updated = data_manager.update_crop(crop_id, crop_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Crop with ID '{crop_id}' not found.")
    return updated

@router.delete("/{crop_id}", summary="Delete a crop from the database")
def delete_crop(crop_id: str):
    success = data_manager.delete_crop(crop_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Crop with ID '{crop_id}' not found.")
    return {"message": f"Crop '{crop_id}' deleted successfully."}
