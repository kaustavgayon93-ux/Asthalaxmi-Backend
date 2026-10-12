from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import Survey, SurveyCreate, SyncBatchRequest
from app.services.data_manager import data_manager

router = APIRouter(prefix="/surveys", tags=["Surveys & CCE"])

@router.get("", response_model=List[Survey], summary="List all field surveys and CCE records")
def get_all_surveys():
    return data_manager.get_surveys()

@router.post("", response_model=Survey, status_code=201, summary="Record a new field survey or CCE trial")
def create_survey(survey_in: SurveyCreate):
    return data_manager.create_survey(survey_in)

@router.post("/sync", response_model=List[Survey], summary="Batch sync offline field surveys collected without cellular network")
def sync_offline_surveys(req: SyncBatchRequest):
    return data_manager.sync_batch_surveys(req.surveys)

@router.delete("/{survey_id}", summary="Delete a survey record")
def delete_survey(survey_id: str):
    success = data_manager.delete_survey(survey_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Survey '{survey_id}' not found.")
    return {"message": f"Survey '{survey_id}' deleted successfully."}
