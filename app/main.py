from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import crops, districts, surveys, forecast, bulletin

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(crops.router, prefix=settings.API_V1_STR)
app.include_router(districts.router, prefix=settings.API_V1_STR)
app.include_router(surveys.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(bulletin.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "challenge": "NESFIC-D-12 (ASSAC / Assam Innovation & Startup Foundation)",
        "docs": "/docs",
        "endpoints": {
            "crops": f"{settings.API_V1_STR}/crops",
            "districts": f"{settings.API_V1_STR}/districts",
            "surveys": f"{settings.API_V1_STR}/surveys",
            "forecast": f"{settings.API_V1_STR}/forecast/predict",
            "cce_calculate": f"{settings.API_V1_STR}/cce/calculate",
            "flood_assessment": f"{settings.API_V1_STR}/flood/assessment",
            "official_bulletin": f"{settings.API_V1_STR}/bulletin/generate"
        }
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
