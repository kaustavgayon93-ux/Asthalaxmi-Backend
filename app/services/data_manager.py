import os
import json
import uuid
from typing import List, Optional, Dict
from app.config import settings
from app.models.schemas import Crop, District, Survey, CropCreate, CropUpdate, DistrictUpdate, SurveyCreate

class DataManager:
    def __init__(self):
        self.crops_file = os.path.join(settings.DATA_DIR, "crops.json")
        self.districts_file = os.path.join(settings.DATA_DIR, "districts.json")
        self.surveys_file = os.path.join(settings.DATA_DIR, "surveys.json")
        
        self.crops: Dict[str, Crop] = {}
        self.districts: Dict[str, District] = {}
        self.surveys: Dict[str, Survey] = {}
        
        self.load_data()

    def load_data(self):
        # Load Crops
        if os.path.exists(self.crops_file):
            with open(self.crops_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                self.crops = {item["id"]: Crop(**item) for item in items}
        
        # Load Districts
        if os.path.exists(self.districts_file):
            with open(self.districts_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                self.districts = {item["id"]: District(**item) for item in items}
        
        # Load Surveys
        if os.path.exists(self.surveys_file):
            with open(self.surveys_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                self.surveys = {item["id"]: Survey(**item) for item in items}

    def save_crops(self):
        with open(self.crops_file, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in self.crops.values()], f, indent=2, ensure_ascii=False)

    def save_districts(self):
        with open(self.districts_file, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in self.districts.values()], f, indent=2, ensure_ascii=False)

    def save_surveys(self):
        with open(self.surveys_file, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in self.surveys.values()], f, indent=2, ensure_ascii=False)

    # --- Crops CRUD ---
    def get_crops(self, category: Optional[str] = None) -> List[Crop]:
        crops_list = list(self.crops.values())
        if category and category != "All Categories":
            return [c for c in crops_list if c.category == category]
        return crops_list

    def get_crop(self, crop_id: str) -> Optional[Crop]:
        return self.crops.get(crop_id)

    def create_crop(self, crop_in: CropCreate) -> Crop:
        crop = Crop(**crop_in.model_dump())
        self.crops[crop.id] = crop
        self.save_crops()
        return crop

    def update_crop(self, crop_id: str, crop_in: CropUpdate) -> Optional[Crop]:
        if crop_id not in self.crops:
            return None
        existing = self.crops[crop_id].model_dump()
        update_data = crop_in.model_dump(exclude_unset=True)
        existing.update(update_data)
        updated = Crop(**existing)
        self.crops[crop_id] = updated
        self.save_crops()
        return updated

    def delete_crop(self, crop_id: str) -> bool:
        if crop_id in self.crops:
            del self.crops[crop_id]
            self.save_crops()
            return True
        return False

    # --- Districts CRUD ---
    def get_districts(self) -> List[District]:
        return list(self.districts.values())

    def get_district(self, district_id: str) -> Optional[District]:
        return self.districts.get(district_id)

    def update_district(self, district_id: str, dist_in: DistrictUpdate) -> Optional[District]:
        if district_id not in self.districts:
            return None
        existing = self.districts[district_id].model_dump()
        update_data = dist_in.model_dump(exclude_unset=True)
        existing.update(update_data)
        updated = District(**existing)
        self.districts[district_id] = updated
        self.save_districts()
        return updated

    # --- Surveys CRUD ---
    def get_surveys(self) -> List[Survey]:
        return list(self.surveys.values())

    def create_survey(self, survey_in: SurveyCreate) -> Survey:
        survey_dict = survey_in.model_dump()
        survey_dict["id"] = f"SRV-{int(uuid.uuid4().hex[:8], 16)}"
        from datetime import datetime, timezone
        survey_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        survey = Survey(**survey_dict)
        self.surveys[survey.id] = survey
        
        # If CCE and synced, increment district target
        if survey.isCCE and survey.syncStatus == "synced":
            if survey.districtId in self.districts:
                d = self.districts[survey.districtId]
                d.cceCompleted += 1
                self.save_districts()
                
        self.save_surveys()
        return survey

    def sync_batch_surveys(self, surveys_in: List[SurveyCreate]) -> List[Survey]:
        results = []
        for s_in in surveys_in:
            s_dict = s_in.model_dump()
            s_dict["id"] = f"SRV-{int(uuid.uuid4().hex[:8], 16)}"
            from datetime import datetime, timezone
            s_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
            s_dict["syncStatus"] = "synced"
            
            survey = Survey(**s_dict)
            self.surveys[survey.id] = survey
            results.append(survey)
            
            if survey.isCCE and survey.districtId in self.districts:
                self.districts[survey.districtId].cceCompleted += 1
                
        self.save_surveys()
        self.save_districts()
        return results

    def delete_survey(self, survey_id: str) -> bool:
        if survey_id in self.surveys:
            del self.surveys[survey_id]
            self.save_surveys()
            return True
        return False

data_manager = DataManager()
