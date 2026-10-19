import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db, SessionLocal
from seed_data import seed_database
from routers import (
    users,
    divisions,
    compartments,
    plantations,
    sample_plots,
    tree_measurements,
    alerts,
    field_inspections,
    carbon_mrv,
    audit_log,
    analytics,
    satellite,
    drone_surveys,
    government_resources,
    ml_models,
    satellite_records,
    carbon_credits,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables and seed realistic data if empty
    init_db()
    db = SessionLocal()
    try:
        db.info["skip_audit"] = True
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="Asthalaxmi API",
    description="FastAPI backend for Asthalaxmi Forest & Plantation Monitoring System (Assam)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (dev open policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(analytics.router)
app.include_router(government_resources.router)
app.include_router(users.router)
app.include_router(divisions.router)
app.include_router(compartments.router)
app.include_router(plantations.router)
app.include_router(sample_plots.router)
app.include_router(tree_measurements.router)
app.include_router(alerts.router)
app.include_router(field_inspections.router)
app.include_router(carbon_mrv.router)
app.include_router(audit_log.router)
app.include_router(satellite.router)
app.include_router(drone_surveys.router)
app.include_router(ml_models.router)
app.include_router(satellite_records.router)
app.include_router(carbon_credits.router)

# Mount local uploads directory for drone files and orthomosaics
uploads_path = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")


@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Asthalaxmi Forest & Plantation Monitoring System",
        "description": "Satellite-based MRV & Plantation Carbon Monitoring for Assam Forest Department / ASSAC",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
