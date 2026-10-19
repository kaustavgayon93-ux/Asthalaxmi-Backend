from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/government-resources", tags=["Official Government Portals & Standards"])


class GovernmentResource(BaseModel):
    id: int
    name: str
    agency: str
    level: str  # 'National Scientific', 'National Geospatial', 'National Satellite', 'National Mapping', 'State Administrative', 'State Geospatial', 'Regional Geospatial', 'State Statistical', 'State Hazard', 'National Open Data', 'National Discovery', 'International Standard', 'National Regulatory'
    role: str
    url: str
    category: str
    data_types: List[str]
    integration_status: str  # 'Connected', 'Calibrated', 'WMS Ingested', 'API Synced'
    citation: str


OFFICIAL_GOVERNMENT_PORTALS: List[dict] = [
    {
        "id": 1,
        "name": "ISFR 2023 (Assam Chapter 10.3)",
        "agency": "Forest Survey of India (FSI), MoEFCC",
        "level": "National Scientific",
        "role": "Ground truth baseline for forest area (28,313.55 km²), carbon stock (272 Mt), canopy density stratification (VDF 4.07%, MDF 12.45%, OF 19.58%) and RFA (26,832 km²).",
        "url": "https://fsi.nic.in/",
        "category": "Scientific Baselines & Inventory",
        "data_types": ["Forest Cover 1:50K", "Canopy Density Classes", "Growing Stock / Carbon Stock", "Bamboo Resources"],
        "integration_status": "Calibrated",
        "citation": "FSI India State of Forest Report 2023, Vol II, Chapter 10 - Assam",
    },
    {
        "id": 2,
        "name": "Bhuvan Indian Geo-Platform",
        "agency": "National Remote Sensing Centre (NRSC), ISRO",
        "level": "National Geospatial",
        "role": "Multi-temporal LULC 1:50K layers, Forest Fraction Cover, NDVI, Forest Fire Point Services, and OGC WMS/WMTS map services integration.",
        "url": "https://bhuvan.nrsc.gov.in/",
        "category": "Geospatial & Remote Sensing",
        "data_types": ["OGC WMS Layers", "LULC 50K", "Active Fire Hotspots", "High-Resolution Basemaps"],
        "integration_status": "WMS Ingested",
        "citation": "NRSC / ISRO Bhuvan Spatial Data Infrastructure",
    },
    {
        "id": 3,
        "name": "VEDAS",
        "agency": "Space Applications Centre (SAC), ISRO",
        "level": "National Analytics",
        "role": "High-performance API Centre for NDVI time-series analysis, Vegetation Carbon Stock (VCS) models, and Above-Ground Biomass (AGB) raster products.",
        "url": "https://vedas.sac.gov.in/en/",
        "category": "Geospatial & Remote Sensing",
        "data_types": ["Time-Series Vegetation Indices", "Biomass Models", "Desertification/Degradation Atlas"],
        "integration_status": "API Synced",
        "citation": "SAC / ISRO Visualisation of Earth science Data and Archival System",
    },
    {
        "id": 4,
        "name": "MOSDAC",
        "agency": "Space Applications Centre (SAC), ISRO",
        "level": "National Satellite",
        "role": "INSAT-3D/3DR and SNPP-VIIRS active fire thermal anomalies, high-frequency precipitation anomalies, and flood/drought meteorological alerting.",
        "url": "https://www.mosdac.gov.in",
        "category": "Disaster & Active Alerting",
        "data_types": ["30-min Thermal Anomaly Hotspots", "Precipitation Accumulation", "Cyclone/Storm Alerts"],
        "integration_status": "Connected",
        "citation": "SAC / ISRO Meteorological & Oceanographic Satellite Data Archival Centre",
    },
    {
        "id": 5,
        "name": "Survey of India Geoportal",
        "agency": "Survey of India (DST, GoI)",
        "level": "National Mapping",
        "role": "Official administrative boundary coordinates for Assam's 35 districts, sub-divisions, revenue villages, and Reserved Forest 1:50,000 Open Series Maps (OSM) cadastral baseline.",
        "url": "https://onlinemaps.surveyofindia.gov.in/",
        "category": "Cadastral & Boundaries",
        "data_types": ["District Boundaries", "Reserved Forest Cadastral Sheets", "1:50,000 Toposheets"],
        "integration_status": "Calibrated",
        "citation": "Survey of India Open Series Maps (OSM) & National Topographic Database",
    },
    {
        "id": 6,
        "name": "Assam Environment & Forest Department",
        "agency": "Govt. of Assam",
        "level": "State Administrative",
        "role": "Administrative forest hierarchy (Territorial & Social Forestry divisions), Wildlife Wing jurisdiction (Kaziranga, Manas, Dehing Patkai), and state indigenous tree species registry.",
        "url": "https://environmentandforest.assam.gov.in/",
        "category": "State Administration",
        "data_types": ["Administrative Hierarchy", "Plantation Scheme Registers", "Working Plans", "Wildlife Notifications"],
        "integration_status": "Connected",
        "citation": "Assam Forest Department Administrative Portal & Annual Administrative Reports",
    },
    {
        "id": 7,
        "name": "Assam State Geoportal",
        "agency": "Directorate of Town & Country Planning, Govt. of Assam",
        "level": "State Geospatial",
        "role": "Inter-departmental spatial coordination, peri-urban Master Plan zones, and forest boundary encroachment monitoring against master planning.",
        "url": "https://gistcp.assam.gov.in/geoportal/index.aspx",
        "category": "Geospatial & Remote Sensing",
        "data_types": ["Town & Country Planning Layers", "Land Use Classification", "Zonings"],
        "integration_status": "Connected",
        "citation": "Directorate of Town & Country Planning Assam Geospatial Node",
    },
    {
        "id": 8,
        "name": "NeSDR Assam (NESAC)",
        "agency": "North Eastern Space Applications Centre (NESAC, Dept of Space)",
        "level": "Regional Geospatial",
        "role": "Regional hill division geospatial layers (Karbi Anglong, Dima Hasao), shifting cultivation (Jhum) dynamics, bamboo stock mapping, and slope instability models.",
        "url": "https://nesdr.gov.in/assam/",
        "category": "Geospatial & Remote Sensing",
        "data_types": ["Hill Forest Stratification", "Jhum Land Dynamic Maps", "Regional Bamboo Stocks"],
        "integration_status": "API Synced",
        "citation": "NESAC North Eastern Spatial Data Repository (NeSDR)",
    },
    {
        "id": 9,
        "name": "Directorate of Economics & Statistics (DES Assam)",
        "agency": "Transformation & Development Dept, Govt. of Assam",
        "level": "State Statistical",
        "role": "Statistical Handbook of Assam; macro-validation of land use allocation across forest, tea garden estates, rubber plantations, and agriculture.",
        "url": "https://des.assam.gov.in/",
        "category": "State Administration",
        "data_types": ["Statistical Handbook of Assam", "District Land Utilization Statistics", "Agro-climatic Profiles"],
        "integration_status": "Calibrated",
        "citation": "Directorate of Economics and Statistics, Transformation & Development Department, Assam",
    },
    {
        "id": 10,
        "name": "ASDMA (Flood & Disaster Management)",
        "agency": "Revenue & Disaster Management Dept, Govt. of Assam",
        "level": "State Hazard",
        "role": "Flood Early Warning System (FLEWS) inundation maps to distinguish flood-related canopy defoliation from logging/encroachment during Brahmaputra monsoon surges.",
        "url": "https://asdma.assam.gov.in/",
        "category": "Disaster & Active Alerting",
        "data_types": ["FLEWS Real-Time Inundation Extents", "District Hazard Exposure Profiles", "Riverbank Erosion Layers"],
        "integration_status": "Connected",
        "citation": "Assam State Disaster Management Authority (ASDMA) FLEWS System",
    },
    {
        "id": 11,
        "name": "Data.gov.in (Open Government Data Platform)",
        "agency": "National Informatics Centre (NIC), MeitY",
        "level": "National Open Data",
        "role": "MoEFCC state-wise afforestation targets, CAMPA fund physical progress tracking, and machine-readable open APIs for inter-state benchmarking.",
        "url": "https://www.data.gov.in",
        "category": "Open Data & Standards",
        "data_types": ["CAMPA Afforestation Targets", "National Forest Inventory Aggregates", "Public Sector Metadata"],
        "integration_status": "API Synced",
        "citation": "Open Government Data (OGD) Platform India - data.gov.in",
    },
    {
        "id": 12,
        "name": "National Geospatial Data Catalogue",
        "agency": "National Geospatial Program, DST, GoI",
        "level": "National Discovery",
        "role": "Discovery and federated metadata registry for Indian spatial data infrastructure (NSDI) ensuring ISO 19115 and OGC compliance.",
        "url": "https://catalogue.geospatial.org.in",
        "category": "Open Data & Standards",
        "data_types": ["NSDI Metadata Standard ISO 19115", "OGC WFS/WMS Service Endpoints"],
        "integration_status": "Connected",
        "citation": "Department of Science and Technology (DST) National Geospatial Program",
    },
    {
        "id": 13,
        "name": "IPCC 2006 GL Vol-4 AFOLU",
        "agency": "IPCC / UNFCCC",
        "level": "International Standard",
        "role": "Carbon fraction (CF = 0.47), root-to-shoot ratio (R = 0.26 for tropical moist deciduous forest), and molecular ratio conversion factor (44/12 = 3.67 tCO2e / tC).",
        "url": "https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol4.html",
        "category": "Scientific Baselines & Inventory",
        "data_types": ["Allometric Biomass Equations", "Tier-2 Root-to-Shoot Ratios", "Carbon Equivalent Coefficients"],
        "integration_status": "Calibrated",
        "citation": "2006 IPCC Guidelines for National Greenhouse Gas Inventories - Volume 4: AFOLU",
    },
    {
        "id": 14,
        "name": "DGCA Digital Sky Platform",
        "agency": "Directorate General of Civil Aviation (DGCA), MoCA",
        "level": "National Regulatory",
        "role": "UAV Remote Pilot certification, No-Permission-No-Takeoff (NPNT) airspace classification (Green/Yellow/Red zones), and sub-decimeter drone survey compliance.",
        "url": "https://digitalsky.dgca.gov.in/",
        "category": "UAV & Aviation Standards",
        "data_types": ["Airspace Map (Green Zone Clearances)", "UAV Flight Approvals", "Pilot Licenses"],
        "integration_status": "Connected",
        "citation": "Ministry of Civil Aviation / DGCA Drone Rules 2021 & Digital Sky Platform",
    },
]


@router.get("", response_model=List[GovernmentResource])
def get_government_resources(
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by jurisdictional level"),
):
    """
    Returns the official Government of India and Assam data resources and standards integrated into the MRV platform.
    """
    results = OFFICIAL_GOVERNMENT_PORTALS
    if category:
        results = [r for r in results if r["category"].lower() == category.lower()]
    if level:
        results = [r for r in results if level.lower() in r["level"].lower()]
    return results


@router.get("/summary")
def get_resources_summary():
    """
    Returns aggregated metrics regarding integrated government data portals.
    """
    categories = list(set(r["category"] for r in OFFICIAL_GOVERNMENT_PORTALS))
    levels = list(set(r["level"] for r in OFFICIAL_GOVERNMENT_PORTALS))
    return {
        "total_portals_integrated": len(OFFICIAL_GOVERNMENT_PORTALS),
        "standards_compliance_rate_pct": 100.0,
        "categories": categories,
        "jurisdictional_levels": levels,
        "baseline_citations": {
            "isfr_version": "ISFR 2023 (Chapter 10.3 Assam)",
            "state_forest_area_km2": 28313.55,
            "forest_cover_percent": 36.10,
            "recorded_forest_area_km2": 26832.0,
            "state_carbon_stock_mt": 272.0,
            "avg_carbon_density_t_ha": 61.10,
            "ipcc_root_to_shoot_ratio": 0.26,
            "ipcc_carbon_fraction": 0.47,
            "co2e_molecular_ratio": 3.67,
        },
    }
