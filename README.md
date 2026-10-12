# GeoCrop-NE: Python FastAPI Backend
### Agricultural Intelligence, SAR Radar Fusion, and Yield Forecasting Engine (NESFIC-D-12 / ASSAC)

This repository contains the backend REST API engine for **GeoCrop-NE**, developed for the Assam State Space Applications Centre (ASSAC), Directorate of Agriculture (Government of Assam), and the Assam Innovation & Startup Foundation under **NESFIC-D-12**.

---

## 📚 Project Documentation & Specifications

The `docs/` directory contains complete reference materials for developers, spatial analysts, and AI agents:
* 📄 **[Product Requirement Document (PRD)](docs/PRD.md):** Complete specifications, user personas, functional/non-functional requirements.
* 🏛️ **[Technical Architecture & Scientific Methodology](docs/ARCHITECTURE.md):** Radar physics, Sentinel-1 SAR cloud penetration, Bayesian uncertainty quantification, and CCE formulas.
* 🌾 **[Assam Agricultural Domain Reference](docs/ASSAM_AGRI_DOMAIN.md):** Comprehensive catalog of all 50+ crops grown in Assam, 6 agro-climatic zones, and 35 districts.
* 🤖 **[AI Session Context & Operational Invariants](docs/AI_SESSION_CONTEXT.md):** Mandatory guidelines, constraints, and architecture rules for future AI coding sessions.

---

## 🚀 Key Modules & Capabilities

* **🌾 Complete Assam Crops Database (`/api/v1/crops`):**
  * Full catalog of 50+ crops grown across Assam's agro-climatic zones with baseline yields, typical moisture percentages, and CCE plot configurations.
* **📍 All 35 Administrative Districts (`/api/v1/districts`):**
  * Spatio-temporal records for all 35 Assam districts including standing acreage, predicted yields, flood losses, and baseline uncertainty margins.
* **🔬 Field Data Collection & Offline Batch Sync (`/api/v1/surveys`):**
  * High-accuracy GNSS GPS geotagging, farmer metadata, and standard $5\,\text{m} \times 5\,\text{m}$ Crop Cutting Experiment (CCE) records.
  * Dedicated `/sync` endpoint for batch synchronizing records captured offline in remote riverine *char* or hill terrains.
* **🎯 Pre-Harvest Yield & Acreage Forecasting (`/api/v1/forecast/predict`):**
  * Pre-harvest horizons at $T-45$, $T-30$, and $T-15$ days before harvest.
  * Bayesian Uncertainty Quantification delivering explicit **$90\%$ and $95\%$ Confidence Intervals** for government procurement planning.
* **🌊 Sentinel-1 SAR Radar Flood Inundation (`/api/v1/flood/assessment`):**
  * All-weather radar backscatter drop analysis quantifying flood-damaged acreage and lost tonnage across Brahmaputra and Barak river basins.
* **📄 Official Assam Agricultural Bulletin Generator (`/api/v1/bulletin/generate`):**
  * Generates formatted, print-ready HTML/PDF agricultural bulletins with official ASSAC headers.

---

## 🛠️ API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status, metadata, and endpoint map |
| `GET` | `/health` | Kubernetes / container health check |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation |
| `GET` | `/api/v1/crops` | List all Assam crops (optional `category` filter) |
| `POST` | `/api/v1/crops` | Create new crop entry |
| `PUT` | `/api/v1/crops/{crop_id}` | Edit crop yield baselines and moisture norms |
| `GET` | `/api/v1/districts` | List all 35 districts with acreage and yields |
| `PUT` | `/api/v1/districts/{dist_id}` | Edit district statistics and recalculate |
| `GET` | `/api/v1/surveys` | List all verified ground-truth and CCE surveys |
| `POST` | `/api/v1/surveys` | Record new field survey with GPS coordinates |
| `POST` | `/api/v1/surveys/sync` | Batch sync offline cached surveys |
| `POST` | `/api/v1/forecast/predict` | Advance pre-harvest forecast with 90% & 95% CIs |
| `POST` | `/api/v1/cce/calculate` | Standard 5x5m CCE formula calculator |
| `GET` | `/api/v1/flood/assessment` | Sentinel-1 SAR radar flood loss metrics |
| `GET` | `/api/v1/bulletin/generate` | Official printable agricultural bulletin |

---

## 💻 Local Development Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Access OpenAPI documentation:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

## 🐳 Docker Deployment

```bash
docker build -t geocrop-backend .
docker run -p 8000:8000 geocrop-backend
```

---

## 🧪 Running Tests

```bash
python -m unittest discover tests
```
