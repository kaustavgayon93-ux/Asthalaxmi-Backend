from fastapi import APIRouter
from app.models.schemas import (
    ForecastRequest,
    ForecastResponse,
    CCECalculationRequest,
    CCECalculationResponse,
)
from app.services.forecast_engine import forecast_engine
from app.services.cce_calculator import cce_calculator
from app.services.sar_flood_service import sar_flood_service

router = APIRouter(tags=["Forecasting & Analytics"])

@router.post("/forecast/predict", response_model=ForecastResponse, summary="Compute pre-harvest yield & production forecast with explicit confidence intervals")
def compute_forecast(req: ForecastRequest):
    return forecast_engine.generate_forecast(req)

@router.post("/cce/calculate", response_model=CCECalculationResponse, summary="Calculate standardized crop yield from 5x5m CCE weights and moisture")
def calculate_cce_yield(req: CCECalculationRequest):
    return cce_calculator.calculate(req)

@router.get("/flood/assessment", summary="Get real-time Sentinel-1 SAR flood inundation and crop loss metrics")
def get_flood_assessment():
    return sar_flood_service.get_flood_assessment()
