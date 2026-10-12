# AI Session Context & Operational Invariants
## Project: GeoCrop-NE (NESFIC-D-12)

> **NOTICE FOR AI ASSISTANTS & AUTOMATED AGENTS:**  
> Read this document before proposing changes, refactoring code, or answering user queries about this codebase. This document defines the strict domain constraints, core architectural invariants, and design rationale for **GeoCrop-NE**.

---

## 1. Project Background

* **Problem Statement:** NESFIC-D-12 under the North East Startup & Fintech Innovation Challenge 2026, delivered via the **Assam Innovation & Startup Foundation** and **Assam State Space Applications Centre (ASSAC)**.
* **Goal:** Improve timeliness, repeatability, and spatial detail of crop-area, yield, and production estimates for planning, procurement (FCI / Food & Civil Supplies), and disaster compensation in Assam.
* **Sister Repositories:**
  * **Frontend (Next.js 14):** [https://github.com/kaustavgayon93-ux/New-Yield-Frontend](https://github.com/kaustavgayon93-ux/New-Yield-Frontend.git)
  * **Backend (FastAPI):** [https://github.com/kaustavgayon93-ux/New-Yield-Backend](https://github.com/kaustavgayon93-ux/New-Yield-Backend.git)

---

## 2. Core Architectural Invariants (DO NOT VIOLATE)

### Invariant 1: The "Monsoon Blocker" & All-Weather Radar
* **Rule:** Never propose an optical-only satellite solution (Sentinel-2, Landsat alone).
* **Rationale:** Assam has $70\%-85\%$ cloud cover during the Kharif season when Sali rice (70% of state crops) is growing. Any solution must incorporate **Sentinel-1 C-Band Synthetic Aperture Radar (SAR)** dual-polarization (VV/VH) backscatter to penetrate monsoon cloud cover.

### Invariant 2: Explicit Uncertainty Quantification (UQ)
* **Rule:** Never display or return a single deterministic number for crop production.
* **Rationale:** Government procurement and food-management agencies cannot act responsibly on black-box point estimates. Every forecast must provide explicit **$90\%$ and $95\%$ Confidence Intervals** (e.g. `Production: 1,842,500 ± 88,400 MT`).

### Invariant 3: 100% In-App Data Editability
* **Rule:** All district baselines, crop parameters, and field survey records must remain fully editable by the user.
* **Rationale:** Departmental officials and agricultural scientists must be able to calibrate models, adjust for localized flood incidents, and update baseline parameters directly in the UI with instant reactive recalculation.

### Invariant 4: Offline-First Field Operation
* **Rule:** Field survey capture and CCE data recording must function with zero network connectivity.
* **Rationale:** Field enumerators operate in remote riverine *chars* and hill tracts without cellular signals. Surveys are cached locally (`pending_offline`) and batch-synced when online.

### Invariant 5: Complete 50+ Assam Crop Diversity
* **Rule:** Do not truncate the crop database to just 2 or 3 crops.
* **Rationale:** Assam has rich agro-biodiversity. The system explicitly maintains full catalogs for Cereals, Oilseeds, Pulses, Commercial/Fibre, Plantation, Fruits, Vegetables, and Spices with local Assamese names (অসমীয়া).

---

## 3. Frontend Architecture (Next.js 14 App Router)

* **Directory Structure:**
  * `src/app/page.tsx`: Top coordinator managing View 1 (Dashboard), View 2 (Mobile App), and View 3 (Crops Directory).
  * `src/context/GeoCropContext.tsx`: Single source of truth. Handles reactive recalculation of total area, yields, production, flood losses, and uncertainty bounds, with automatic persistence to `localStorage`.
  * `src/components/GisMap.tsx`: Dynamic client-side Leaflet component (`ssr: false`) rendering district boundaries, Sentinel-1 SAR flood overlays, and CCE pins.
  * `src/components/Charts.tsx`: Chart.js rendering production bar charts and Gaussian uncertainty probability density curves.
  * `src/components/MobileCollector.tsx`: Realistic smartphone simulator with 5x5m CCE yield formula and offline queue.
  * `src/components/CropsDirectory.tsx`: Searchable 50+ crop cards with parameter editors.
  * `src/components/Modals.tsx`: Full edit modals for districts and crops.

---

## 4. Backend Architecture (FastAPI + Python 3.12)

* **Directory Structure:**
  * `app/main.py`: Application entrypoint, CORS configuration, Swagger docs (`/docs`).
  * `app/models/schemas.py`: Pydantic validation models.
  * `app/services/forecast_engine.py`: Hybrid AI + Biophysical model with Bayesian uncertainty bounds.
  * `app/services/cce_calculator.py`: Standardized DES/ASSAC 5x5m CCE formula with moisture correction factor.
  * `app/services/sar_flood_service.py`: SAR flood extent intersection calculator.
  * `app/services/data_manager.py`: Persistent CRUD engine storing data in `app/data/`.
  * `app/routers/`: Individual API endpoints (`crops.py`, `districts.py`, `surveys.py`, `forecast.py`, `bulletin.py`).

---

## 5. Development & Testing Commands

* **Run Frontend:**
  ```bash
  cd geocrop-nextjs
  npm install
  npm run dev
  # Runs at http://localhost:3000
  ```

* **Run Backend:**
  ```bash
  cd geocrop-backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  # Swagger at http://localhost:8000/docs
  ```

* **Run Backend Unit Tests:**
  ```bash
  python -m unittest tests/test_api.py
  ```
