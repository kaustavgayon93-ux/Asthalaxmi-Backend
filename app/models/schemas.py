from typing import List, Optional, Tuple, Literal
from pydantic import BaseModel, Field

# --- Crop Schemas ---
class CropBase(BaseModel):
    name: str
    assameseName: str
    scientificName: str
    category: str
    season: str
    sowingPeriod: str
    harvestPeriod: str
    avgYield: float = Field(..., description="Average baseline yield in tonnes per hectare (t/ha)")
    typicalMoisture: float = Field(..., description="Standard moisture percentage at harvest")
    ccePlotSize: str = Field(default="5m x 5m", description="Standardized CCE plot size")
    growthDurationDays: int
    color: str = "#22c55e"
    notes: Optional[str] = None

class CropCreate(CropBase):
    id: str

class CropUpdate(BaseModel):
    name: Optional[str] = None
    assameseName: Optional[str] = None
    avgYield: Optional[float] = None
    typicalMoisture: Optional[float] = None
    growthDurationDays: Optional[int] = None
    season: Optional[str] = None
    notes: Optional[str] = None

class Crop(CropBase):
    id: str

    class Config:
        from_attributes = True


# --- District Schemas ---
class DistrictBase(BaseModel):
    name: str
    assameseName: str
    hq: str
    zone: str
    coordinates: List[float] = Field(..., description="[Latitude, Longitude]")
    baselineCroppedAreaHa: float
    currentCroppedAreaHa: float
    predictedAvgYield: float
    floodVulnerability: Literal["High", "Moderate", "Low"]
    floodDamagedHa: float
    uncertaintyMarginPct: float
    cceTarget: int
    cceCompleted: int = 0
    primaryCrops: List[str] = []

class DistrictUpdate(BaseModel):
    currentCroppedAreaHa: Optional[float] = None
    predictedAvgYield: Optional[float] = None
    floodDamagedHa: Optional[float] = None
    uncertaintyMarginPct: Optional[float] = None
    floodVulnerability: Optional[Literal["High", "Moderate", "Low"]] = None
    cceCompleted: Optional[int] = None
    cceTarget: Optional[int] = None

class District(DistrictBase):
    id: str

    class Config:
        from_attributes = True


# --- Field Survey & CCE Schemas ---
class CCEDetails(BaseModel):
    plotSize: str = "5m x 5m (25 sq.m)"
    freshBiomassKg: float
    freshGrainKg: float
    moisturePct: float
    calculatedYieldTHa: float
    scalePhotoUrl: Optional[str] = None
    fieldPhotoUrl: Optional[str] = None

class SurveyCreate(BaseModel):
    enumeratorName: str
    phone: str
    districtId: str
    blockName: str
    villageName: str
    farmerName: str
    farmerId: Optional[str] = None
    cropId: str
    sowingDate: str
    stage: str
    irrigation: str = "Canal & Rainfed"
    healthStatus: str = "Healthy"
    damageNote: Optional[str] = None
    coordinates: List[float]
    accuracyMeters: float
    isCCE: bool = False
    cceDetails: Optional[CCEDetails] = None
    syncStatus: Literal["synced", "pending_offline"] = "synced"

class Survey(SurveyCreate):
    id: str
    timestamp: str

    class Config:
        from_attributes = True

class SyncBatchRequest(BaseModel):
    surveys: List[SurveyCreate]


# --- Forecasting & Uncertainty Schemas ---
class ForecastRequest(BaseModel):
    districtId: str = Field(default="all", description="'all' or specific district ID")
    cropId: str = Field(default="crop_sali_rice", description="Target crop ID")
    leadTimeDays: int = Field(default=30, description="Lead time in days: 45, 30, or 15 days pre-harvest")

class ConfidenceInterval(BaseModel):
    lower: float
    upper: float

class ForecastResponse(BaseModel):
    forecastId: str
    timestamp: str
    crop: str
    season: str
    leadTimeDays: int
    leadTimeLabel: str
    scope: str
    totalAreaHa: float
    avgYieldTHa: float
    totalProductionTonnes: float
    uncertaintyMarginPct: float
    confidenceInterval90: ConfidenceInterval
    confidenceInterval95: ConfidenceInterval
    floodDamagedHa: float
    estimatedLostProductionTonnes: float
    cceProgressPct: float
    modelMetrics: dict


# --- CCE Calculation Schemas ---
class CCECalculationRequest(BaseModel):
    freshGrainKg: float
    moisturePct: float
    standardMoisturePct: float = 14.0
    plotAreaSqM: float = 25.0

class CCECalculationResponse(BaseModel):
    calculatedYieldTHa: float
    adjustedMoistureFactor: float
    dryGrainEquivalentKg: float
