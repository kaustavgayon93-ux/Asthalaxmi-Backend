# Asthalaxmi Forest & Plantation Monitoring Backend (Assam)

High-performance **FastAPI** backend powering the **Asthalaxmi Forest & Plantation Monitoring Dashboard** for the State of Assam, India.

Designed to address **NESFIC-D-15** indicative technology directions:
- Optical & SAR remote sensing fusion (overcoming monsoon cloud occlusion)
- Sub-decimeter UAV Canopy Height Model (CHM) integration
- Individual Tree Detection (ITD) & Crown Segmentation (DeepForest-v2)
- Allometric biomass & carbon prediction calibrated to FSI NFI Tier-2
- Cryptographic SHA-256 audit trails & IPCC AFOLU Tier-2 Carbon Accounting

---

## Tech Stack & Architecture

- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Database**: SQLite (`asthalaxmi.db`) with full foreign key constraints
- **Server**: Uvicorn ASGI

---

## Directory Structure

```
backend/
├── main.py                          # FastAPI application, CORS, lifespan & router registration
├── database.py                      # SQLAlchemy engine, session factory, Base & init_db()
├── models.py                        # Complete database models (13 tables)
├── schemas.py                       # Pydantic request/response schemas
├── audit_listener.py                # Automatic SQLAlchemy event listener for audit logging
├── seed_data.py                     # Realistic Assam division, compartment & plantation data
├── seed_satellite.py                # Synthetic Aperture Radar (SAR) & Sentinel-2 scene catalog
├── seed_satellite_and_carbon.py     # Carbon credit & MRV initial datasets
├── enrich_multisensor_data.py       # Multi-sensor radar & drone fusion enrichment
├── asthalaxmi.db                    # Pre-seeded SQLite database with zero FK violations
├── requirements.txt                 # Python dependencies
└── routers/
    ├── analytics.py                 # Summary metrics & dashboard KPI aggregations
    ├── alerts.py                    # Real-time deforestation alerts & GeoJSON
    ├── audit_log.py                 # Cryptographic system audit trail
    ├── carbon_credits.py            # Verified carbon credits, issuance & /summary
    ├── carbon_mrv.py                # IPCC 2006 AFOLU Tier-2 carbon accounting engine
    ├── compartments.py              # Compartment boundaries, canopy density & GeoJSON
    ├── divisions.py                 # Forest divisions & circle administration
    ├── drone_surveys.py             # UAV orthomosaics, mission flightlogs & AI crown count
    ├── field_inspections.py         # Ground verification reports & photo dossiers
    ├── government_resources.py      # National/state portal registry & ISFR standards
    ├── ml_models.py                 # AI/ML multi-sensor biomass & crown detection
    ├── plantations.py               # Afforestation schemes (CAMPA, NABARD) & survival tracking
    ├── sample_plots.py              # Permanent/temporary forest inventory plots
    ├── satellite.py                 # STAC catalog & Sentinel-1 SAR scene queries
    ├── satellite_records.py         # Temporal radar backscatter records
    ├── tree_measurements.py         # GBH/DBH, height & species inventory
    └── users.py                     # Role-based access control (DFO, RFO, Scientist, Guard)
```

---

## Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/kaustavgayon93-ux/Asthalaxmi-Backend.git
cd Asthalaxmi-Backend
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Server
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## Verified Endpoints & Actions

- `GET /api/analytics/dashboard` — High-level forest cover, carbon, and alert metrics
- `GET /api/compartments/geojson` — Spatial polygon boundaries for Assam forest compartments
- `GET /api/plantations/geojson` — Afforestation plots with survival rates
- `GET /api/alerts/geojson` — Real-time canopy loss and boundary encroachment incidents
- `POST /api/drone-surveys/{id}/run-ai-crown-count` — Automated tree crown segmentation
- `POST /api/carbon-reports/calculate-ipcc` — 5-step IPCC 2006 AFOLU Tier-2 Carbon Equation
- `POST /api/ml/predict-biomass` — Multi-sensor optical/SAR fusion biomass model
- `POST /api/ml/segment-trees` — DeepForest tree crown detection
