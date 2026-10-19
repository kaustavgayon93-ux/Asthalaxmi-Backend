from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


# -------------------------------------------------------------
# User Schemas
# -------------------------------------------------------------
class UserBase(BaseModel):
    name: str
    role: str  # 'ASSAC_SCIENTIST', 'DFO', 'RFO', 'BEAT_GUARD', 'AUDITOR'
    email: str
    phone: str
    assigned_division: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    assigned_division: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Division Schemas
# -------------------------------------------------------------
class DivisionBase(BaseModel):
    name: str
    code: str
    circle_name: str
    state: str = "Assam"
    total_area_ha: float
    forest_cover_percent: float
    num_ranges: int
    vdf_area_ha: Optional[float] = None
    mdf_area_ha: Optional[float] = None
    of_area_ha: Optional[float] = None
    carbon_stock_mt: Optional[float] = None
    boundary_source: Optional[str] = "Survey of India OSM 1:50K / FSI ISFR 2023"
    headquarters: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    satellite_sync_status: Optional[str] = None
    last_satellite_pass: Optional[datetime] = None
    satellite_ndvi: Optional[float] = None
    satellite_sar_vh: Optional[float] = None


class DivisionCreate(DivisionBase):
    pass


class DivisionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    circle_name: Optional[str] = None
    state: Optional[str] = None
    total_area_ha: Optional[float] = None
    forest_cover_percent: Optional[float] = None
    num_ranges: Optional[int] = None
    vdf_area_ha: Optional[float] = None
    mdf_area_ha: Optional[float] = None
    of_area_ha: Optional[float] = None
    carbon_stock_mt: Optional[float] = None
    boundary_source: Optional[str] = None
    headquarters: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    satellite_sync_status: Optional[str] = None
    last_satellite_pass: Optional[datetime] = None
    satellite_ndvi: Optional[float] = None
    satellite_sar_vh: Optional[float] = None


class DivisionResponse(DivisionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    compartment_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Compartment Schemas
# -------------------------------------------------------------
class CompartmentBase(BaseModel):
    division_id: str
    division_code: str
    range_name: str
    beat_name: str
    compartment_number: str
    boundary_geojson: str
    centroid_lat: float
    centroid_lng: float
    total_area_ha: float
    forest_type: str
    canopy_density_percent: float
    mean_ndvi: Optional[float] = None
    mean_ndwi: Optional[float] = None
    cir_index: Optional[float] = None
    sar_vh_backscatter_db: Optional[float] = None
    canopy_height_m: Optional[float] = None
    biomass_tonnes_per_ha: Optional[float] = None


class CompartmentCreate(CompartmentBase):
    pass


class CompartmentUpdate(BaseModel):
    division_id: Optional[str] = None
    division_code: Optional[str] = None
    range_name: Optional[str] = None
    beat_name: Optional[str] = None
    compartment_number: Optional[str] = None
    boundary_geojson: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    total_area_ha: Optional[float] = None
    forest_type: Optional[str] = None
    canopy_density_percent: Optional[float] = None
    mean_ndvi: Optional[float] = None
    mean_ndwi: Optional[float] = None
    cir_index: Optional[float] = None
    sar_vh_backscatter_db: Optional[float] = None
    canopy_height_m: Optional[float] = None
    biomass_tonnes_per_ha: Optional[float] = None


class CompartmentResponse(CompartmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Plantation Schemas
# -------------------------------------------------------------
class PlantationBase(BaseModel):
    compartment_id: str
    name: str
    scheme_name: str
    planting_year: int
    primary_species: str
    secondary_species: Optional[str] = None
    initial_saplings: int
    surviving_count: Optional[int] = None
    survival_rate_percent: Optional[float] = None
    area_ha: float
    centroid_lat: float
    centroid_lng: float
    plot_boundary_geojson: Optional[str] = None
    current_ndvi: Optional[float] = None
    current_ndwi: Optional[float] = None
    cir_vigor_score: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    mean_canopy_height_m: Optional[float] = None
    biomass_tonnes_per_ha: Optional[float] = None
    status: str = "Active"


class PlantationCreate(PlantationBase):
    pass


class PlantationUpdate(BaseModel):
    compartment_id: Optional[str] = None
    name: Optional[str] = None
    scheme_name: Optional[str] = None
    planting_year: Optional[int] = None
    primary_species: Optional[str] = None
    secondary_species: Optional[str] = None
    initial_saplings: Optional[int] = None
    surviving_count: Optional[int] = None
    survival_rate_percent: Optional[float] = None
    area_ha: Optional[float] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    plot_boundary_geojson: Optional[str] = None
    current_ndvi: Optional[float] = None
    current_ndwi: Optional[float] = None
    cir_vigor_score: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    mean_canopy_height_m: Optional[float] = None
    biomass_tonnes_per_ha: Optional[float] = None
    status: Optional[str] = None


class PlantationResponse(PlantationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# SamplePlot Schemas
# -------------------------------------------------------------
class SamplePlotBase(BaseModel):
    plantation_id: str
    plot_code: str
    center_lat: float
    center_lng: float
    radius_meters: float = 17.84
    area_ha: float = 0.1
    last_surveyed: Optional[datetime] = None
    survey_count: int = 0
    assigned_guard_id: Optional[str] = None
    status: str = "Active"


class SamplePlotCreate(SamplePlotBase):
    pass


class SamplePlotUpdate(BaseModel):
    plantation_id: Optional[str] = None
    plot_code: Optional[str] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius_meters: Optional[float] = None
    area_ha: Optional[float] = None
    last_surveyed: Optional[datetime] = None
    survey_count: Optional[int] = None
    assigned_guard_id: Optional[str] = None
    status: Optional[str] = None


class SamplePlotResponse(SamplePlotBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# TreeMeasurement Schemas
# -------------------------------------------------------------
class TreeMeasurementBase(BaseModel):
    sample_plot_id: str
    tree_number: int
    species_code: str
    species_local_name: str
    species_botanical_name: str
    gbh_cm: float
    dbh_cm: Optional[float] = None
    height_m: float
    health_status: str = "Healthy"
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None


class TreeMeasurementCreate(TreeMeasurementBase):
    pass


class TreeMeasurementUpdate(BaseModel):
    sample_plot_id: Optional[str] = None
    tree_number: Optional[int] = None
    species_code: Optional[str] = None
    species_local_name: Optional[str] = None
    species_botanical_name: Optional[str] = None
    gbh_cm: Optional[float] = None
    dbh_cm: Optional[float] = None
    height_m: Optional[float] = None
    health_status: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None


class TreeMeasurementResponse(TreeMeasurementBase):
    id: str
    dbh_cm: float
    recorded_at: datetime
    plot_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# AlertIncident Schemas
# -------------------------------------------------------------
class AlertIncidentBase(BaseModel):
    compartment_id: str
    alert_type: str
    severity: str
    centroid_lat: float
    centroid_lng: float
    affected_area_ha: float
    confidence_score: float
    status: str = "Generated"
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    description: str
    detected_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    satellite_scene_id: Optional[str] = None


class AlertIncidentCreate(AlertIncidentBase):
    pass


class AlertIncidentUpdate(BaseModel):
    compartment_id: Optional[str] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    affected_area_ha: Optional[float] = None
    confidence_score: Optional[float] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    description: Optional[str] = None
    detected_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    satellite_scene_id: Optional[str] = None


class AlertStatusUpdate(BaseModel):
    status: str


class AlertAssignUpdate(BaseModel):
    assigned_to: str
    assigned_by: Optional[str] = None


class AlertIncidentResponse(AlertIncidentBase):
    id: str
    detected_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# FieldInspection Schemas
# -------------------------------------------------------------
class FieldInspectionBase(BaseModel):
    alert_id: str
    officer_id: str
    cause: str
    verified_lat: float
    verified_lng: float
    photo_urls: str = "[]"
    remarks: str
    action_taken: Optional[str] = None
    inspection_date: Optional[datetime] = None
    synced_at: Optional[datetime] = None


class FieldInspectionCreate(FieldInspectionBase):
    pass


class FieldInspectionUpdate(BaseModel):
    alert_id: Optional[str] = None
    officer_id: Optional[str] = None
    cause: Optional[str] = None
    verified_lat: Optional[float] = None
    verified_lng: Optional[float] = None
    photo_urls: Optional[str] = None
    remarks: Optional[str] = None
    action_taken: Optional[str] = None
    inspection_date: Optional[datetime] = None
    synced_at: Optional[datetime] = None


class FieldInspectionResponse(FieldInspectionBase):
    id: str
    inspection_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# CarbonMRVReport Schemas
# -------------------------------------------------------------
class CarbonMRVReportBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    compartment_id: Optional[str] = None
    plantation_id: Optional[str] = None
    report_type: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    total_agb_tonnes: float
    agb_per_ha: float
    carbon_stock_tco2e: float
    uncertainty_percent: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    methodology: str = "Verra VM0045"
    model_version: str
    satellite_scenes_used: str = "[]"
    sample_plots_used: int
    sha256_hash: Optional[str] = None
    status: str = "Draft"
    generated_by: Optional[str] = None


class CarbonMRVReportCreate(CarbonMRVReportBase):
    pass


class CarbonMRVReportUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    compartment_id: Optional[str] = None
    plantation_id: Optional[str] = None
    report_type: Optional[str] = None
    reporting_period_start: Optional[datetime] = None
    reporting_period_end: Optional[datetime] = None
    total_agb_tonnes: Optional[float] = None
    agb_per_ha: Optional[float] = None
    carbon_stock_tco2e: Optional[float] = None
    uncertainty_percent: Optional[float] = None
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    methodology: Optional[str] = None
    model_version: Optional[str] = None
    satellite_scenes_used: Optional[str] = None
    sample_plots_used: Optional[int] = None
    sha256_hash: Optional[str] = None
    status: Optional[str] = None
    generated_by: Optional[str] = None


class CarbonMRVReportResponse(CarbonMRVReportBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# AuditLog Schemas
# -------------------------------------------------------------
class AuditLogBase(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    changed_by: str
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    description: str
    ip_address: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Analytics Dashboard Schemas
# -------------------------------------------------------------
class DashboardSummaryResponse(BaseModel):
    total_forest_area_ha: float
    total_plantations: int
    active_alerts: dict[str, int]
    total_carbon_stock_tco2e: float
    total_sample_plots: int
    total_tree_measurements: int
    total_divisions: int
    total_compartments: int
    avg_survival_rate: float
    avg_ndvi: float
    alerts_by_type: dict[str, int]
    alerts_by_status: dict[str, int]
    plantations_by_scheme: dict[str, int]
    plantations_by_year: dict[str, int]
    species_distribution: dict[str, int]
    recent_alerts: List[AlertIncidentResponse]
    recent_inspections: List[FieldInspectionResponse]
    biomass_by_division: dict[str, float]


# -------------------------------------------------------------
# Satellite & Earth Observation Schemas
# -------------------------------------------------------------
class SatelliteSceneBase(BaseModel):
    scene_id: str
    satellite_name: str
    sensor_type: str
    acquisition_date: datetime
    cloud_cover_percent: float = 0.0
    resolution_meters: float = 10.0
    polarization_or_bands: str
    orbit_pass: str = "Descending"
    division_name: str = "All Divisions"
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    area_ha: Optional[float] = None
    processing_level: str = "Level-2A"
    cloud_masked: bool = False
    fusion_status: str = "Raw Ingested"
    footprint_geojson: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    sar_backscatter_vv_db: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    sar_vh_vv_ratio: Optional[float] = None
    ndvi_mean: Optional[float] = None
    ndvi_change: Optional[float] = None
    ndwi_mean: Optional[float] = None
    cir_reflectance: Optional[float] = None
    chm_mean_height_m: Optional[float] = None
    agb_density_t_ha: Optional[float] = None
    cloud_penetration_verified: bool = False
    data_source: Optional[str] = None


class SatelliteSceneCreate(SatelliteSceneBase):
    pass


class SatelliteSceneUpdate(BaseModel):
    satellite_name: Optional[str] = None
    sensor_type: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    cloud_cover_percent: Optional[float] = None
    resolution_meters: Optional[float] = None
    polarization_or_bands: Optional[str] = None
    orbit_pass: Optional[str] = None
    division_name: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    area_ha: Optional[float] = None
    processing_level: Optional[str] = None
    cloud_masked: Optional[bool] = None
    fusion_status: Optional[str] = None
    footprint_geojson: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    sar_backscatter_vv_db: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    sar_vh_vv_ratio: Optional[float] = None
    ndvi_mean: Optional[float] = None
    ndvi_change: Optional[float] = None
    ndwi_mean: Optional[float] = None
    cir_reflectance: Optional[float] = None
    chm_mean_height_m: Optional[float] = None
    agb_density_t_ha: Optional[float] = None
    cloud_penetration_verified: Optional[bool] = None
    data_source: Optional[str] = None


class SatelliteSceneResponse(SatelliteSceneBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SatelliteLayerMetadata(BaseModel):
    id: str
    name: str
    category: str  # 'Base Satellite', 'Spectral Index', 'SAR Radar (All-Weather)', 'AI Derived'
    satellite: str  # 'Sentinel-2', 'Sentinel-1', 'NASA GEDI', 'Copernicus DEM'
    description: str
    tile_url: str
    resolution: str
    cloud_penetrating: bool
    color_scale: Optional[dict] = None
    units: Optional[str] = None


class TemporalComparisonItem(BaseModel):
    period: str  # e.g., 'Pre-Monsoon 2024', 'Post-Monsoon 2024'
    date_range: str
    satellite_used: str
    avg_ndvi: float
    avg_sar_backscatter_db: float
    estimated_canopy_cover_pct: float
    cloud_cover_mitigated_pct: float


class TemporalComparisonResponse(BaseModel):
    division: str
    comparisons: List[TemporalComparisonItem]
    change_summary: str
    canopy_loss_ha: float
    growth_gain_ha: float
    net_change_ha: float


# -------------------------------------------------------------
# Drone (UAV) Survey Schemas
# -------------------------------------------------------------
class DroneSurveyBase(BaseModel):
    mission_code: str
    survey_name: str
    division_name: str
    compartment_id: Optional[str] = None
    plantation_id: Optional[str] = None
    flight_date: datetime
    uav_model: str = "DJI Matrice 350 RTK"
    sensor_type: str = "Multispectral RedEdge-P"
    flight_altitude_m: float = 90.0
    ground_sampling_distance_cm: float = 2.5
    covered_area_ha: float = 45.0
    centroid_lat: float
    centroid_lng: float
    flight_footprint_geojson: Optional[str] = None
    orthomosaic_url: Optional[str] = None
    chm_url: Optional[str] = None
    flight_log_url: Optional[str] = None
    point_cloud_url: Optional[str] = None
    boundary_file_url: Optional[str] = None
    itc_crown_count: int = 0
    survival_rate_verified_pct: float = 0.0
    mean_canopy_height_m: float = 4.5
    biomass_estimate_t_ha: float = 85.0
    mean_ndvi: Optional[float] = 0.82
    mean_ndwi: Optional[float] = 0.28
    cir_reflectance: Optional[float] = 2.45
    sar_correlation_vh_db: Optional[float] = -15.2
    processing_status: str = "Raw Uploaded"
    pilot_in_command: str = "ASSAC Drone Remote Sensing Unit"
    privacy_tier: str = "Department Confidential"
    data_classification: str = "DGCA Compliant / Green Zone"
    notes: Optional[str] = None


class DroneSurveyCreate(DroneSurveyBase):
    pass


class DroneSurveyUpdate(BaseModel):
    survey_name: Optional[str] = None
    division_name: Optional[str] = None
    compartment_id: Optional[str] = None
    plantation_id: Optional[str] = None
    flight_date: Optional[datetime] = None
    uav_model: Optional[str] = None
    sensor_type: Optional[str] = None
    flight_altitude_m: Optional[float] = None
    ground_sampling_distance_cm: Optional[float] = None
    covered_area_ha: Optional[float] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    flight_footprint_geojson: Optional[str] = None
    orthomosaic_url: Optional[str] = None
    chm_url: Optional[str] = None
    flight_log_url: Optional[str] = None
    point_cloud_url: Optional[str] = None
    boundary_file_url: Optional[str] = None
    itc_crown_count: Optional[int] = None
    survival_rate_verified_pct: Optional[float] = None
    mean_canopy_height_m: Optional[float] = None
    biomass_estimate_t_ha: Optional[float] = None
    mean_ndvi: Optional[float] = None
    mean_ndwi: Optional[float] = None
    cir_reflectance: Optional[float] = None
    sar_correlation_vh_db: Optional[float] = None
    processing_status: Optional[str] = None
    pilot_in_command: Optional[str] = None
    privacy_tier: Optional[str] = None
    data_classification: Optional[str] = None
    notes: Optional[str] = None


class DroneSurveyResponse(DroneSurveyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Satellite Record Schemas (Optical & SAR Multi-Sensor)
# -------------------------------------------------------------
class SatelliteRecordBase(BaseModel):
    scene_id: str
    satellite_name: str
    sensor_type: str
    acquisition_date: datetime
    cloud_cover_percent: float = 0.0
    resolution_meters: float = 10.0
    polarization_or_bands: str = "VV, VH, VV/VH"
    orbit_pass: str = "Descending"
    division_name: str = "All Divisions"
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    area_ha: Optional[float] = None
    processing_level: str = "Level-2A"
    cloud_masked: bool = False
    fusion_status: str = "Raw Ingested"
    footprint_geojson: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    ndvi_mean: Optional[float] = None
    ndvi_change: Optional[float] = None
    ndwi_mean: Optional[float] = None
    cir_reflectance: Optional[float] = None
    sar_backscatter_vv_db: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    sar_vh_vv_ratio: Optional[float] = None
    chm_mean_height_m: Optional[float] = None
    agb_density_t_ha: Optional[float] = None
    cloud_penetration_verified: bool = False
    data_source: Optional[str] = "Bhuvan NRSC / VEDAS SAC / Sentinel Hub"


class SatelliteRecordCreate(SatelliteRecordBase):
    pass


class SatelliteRecordUpdate(BaseModel):
    satellite_name: Optional[str] = None
    sensor_type: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    cloud_cover_percent: Optional[float] = None
    resolution_meters: Optional[float] = None
    polarization_or_bands: Optional[str] = None
    orbit_pass: Optional[str] = None
    division_name: Optional[str] = None
    centroid_lat: Optional[float] = None
    centroid_lng: Optional[float] = None
    area_ha: Optional[float] = None
    processing_level: Optional[str] = None
    cloud_masked: Optional[bool] = None
    fusion_status: Optional[str] = None
    footprint_geojson: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    ndvi_mean: Optional[float] = None
    ndvi_change: Optional[float] = None
    ndwi_mean: Optional[float] = None
    cir_reflectance: Optional[float] = None
    sar_backscatter_vv_db: Optional[float] = None
    sar_backscatter_vh_db: Optional[float] = None
    sar_vh_vv_ratio: Optional[float] = None
    chm_mean_height_m: Optional[float] = None
    agb_density_t_ha: Optional[float] = None
    cloud_penetration_verified: Optional[bool] = None
    data_source: Optional[str] = None


class SatelliteRecordResponse(SatelliteRecordBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Carbon Credit Assessment Schemas (Full Traceability)
# -------------------------------------------------------------
class CarbonCreditBase(BaseModel):
    assessment_id: str
    division_name: str
    period_start: datetime
    period_end: datetime
    baseline_carbon_t: float
    current_carbon_t: float
    net_carbon_change_t: float
    eligible_credits_tco2e: float
    methodology: str = "IPCC 2006 Vol-4 AFOLU Tier-2 / Verra VM0045"
    standard: str = "Verra VCS"
    verifier_name: str = "Bureau Veritas India"
    serial_number: Optional[str] = None
    status: str = "Verified"
    sha256_hash: Optional[str] = None
    data_source: Optional[str] = "ISFR 2023 Baseline + Multi-Sensor MRV"


class CarbonCreditCreate(CarbonCreditBase):
    pass


class CarbonCreditResponse(CarbonCreditBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


