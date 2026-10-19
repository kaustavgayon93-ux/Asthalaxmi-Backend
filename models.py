import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    Integer,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


def default_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=default_uuid)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'ASSAC_SCIENTIST', 'DFO', 'RFO', 'BEAT_GUARD', 'AUDITOR'
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    assigned_division = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    assigned_plots = relationship("SamplePlot", back_populates="assigned_guard", foreign_keys="SamplePlot.assigned_guard_id")
    assigned_alerts = relationship("AlertIncident", back_populates="assigned_user", foreign_keys="AlertIncident.assigned_to")
    created_alerts = relationship("AlertIncident", back_populates="creator_user", foreign_keys="AlertIncident.assigned_by")
    field_inspections = relationship("FieldInspection", back_populates="officer")
    carbon_reports = relationship("CarbonMRVReport", back_populates="generator")


class Division(Base):
    __tablename__ = "divisions"

    id = Column(String(36), primary_key=True, default=default_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    circle_name = Column(String(255), nullable=False)
    state = Column(String(100), default="Assam", nullable=False)
    total_area_ha = Column(Float, nullable=False)
    forest_cover_percent = Column(Float, nullable=False)
    num_ranges = Column(Integer, nullable=False)
    vdf_area_ha = Column(Float, default=0.0, nullable=True)
    mdf_area_ha = Column(Float, default=0.0, nullable=True)
    of_area_ha = Column(Float, default=0.0, nullable=True)
    carbon_stock_mt = Column(Float, default=0.0, nullable=True)
    boundary_source = Column(String(255), default="Survey of India OSM 1:50K / FSI ISFR 2023", nullable=True)
    headquarters = Column(String(100), nullable=True)
    centroid_lat = Column(Float, default=26.1852, nullable=True)
    centroid_lng = Column(Float, default=91.7539, nullable=True)
    satellite_sync_status = Column(String(100), default="Live Synced (Sentinel-2 L2A)", nullable=True)
    last_satellite_pass = Column(DateTime, default=utc_now, nullable=True)
    satellite_ndvi = Column(Float, default=0.76, nullable=True)
    satellite_sar_vh = Column(Float, default=-12.5, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    compartments = relationship("Compartment", back_populates="division", cascade="all, delete-orphan")


class Compartment(Base):
    __tablename__ = "compartments"

    id = Column(String(36), primary_key=True, default=default_uuid)
    division_id = Column(String(36), ForeignKey("divisions.id", ondelete="CASCADE"), nullable=False)
    division_code = Column(String(50), nullable=False)
    range_name = Column(String(255), nullable=False)
    beat_name = Column(String(255), nullable=False)
    compartment_number = Column(String(100), nullable=False)
    boundary_geojson = Column(Text, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    total_area_ha = Column(Float, nullable=False)
    forest_type = Column(String(100), nullable=False)  # 'Tropical Moist Deciduous', 'Tropical Semi-Evergreen', etc.
    canopy_density_percent = Column(Float, nullable=False)
    mean_ndvi = Column(Float, nullable=True)  # NDVI (Vegetation Vigor: 0.0 - 1.0)
    mean_ndwi = Column(Float, nullable=True)  # NDWI (Canopy Moisture & Fire Hazard)
    cir_index = Column(Float, nullable=True)  # False Color Infrared Ratio (NIR/Red)
    sar_vh_backscatter_db = Column(Float, nullable=True)  # Sentinel-1 C-band SAR cross-pol (dB)
    canopy_height_m = Column(Float, nullable=True)  # 10m Canopy Height Model (CHM meters)
    biomass_tonnes_per_ha = Column(Float, nullable=True)  # Aboveground Biomass (t/ha)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    division = relationship("Division", back_populates="compartments")
    plantations = relationship("Plantation", back_populates="compartment", cascade="all, delete-orphan")
    alerts = relationship("AlertIncident", back_populates="compartment", cascade="all, delete-orphan")
    carbon_reports = relationship("CarbonMRVReport", back_populates="compartment")


class Plantation(Base):
    __tablename__ = "plantations"

    id = Column(String(36), primary_key=True, default=default_uuid)
    compartment_id = Column(String(36), ForeignKey("compartments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    scheme_name = Column(String(100), nullable=False)  # 'CAMPA', 'State Social Forestry', 'NABARD', etc.
    planting_year = Column(Integer, nullable=False)
    primary_species = Column(String(100), nullable=False)
    secondary_species = Column(String(100), nullable=True)
    initial_saplings = Column(Integer, nullable=False)
    surviving_count = Column(Integer, nullable=True)
    survival_rate_percent = Column(Float, nullable=True)
    area_ha = Column(Float, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    plot_boundary_geojson = Column(Text, nullable=True)
    current_ndvi = Column(Float, nullable=True)  # NDVI (Vegetation Vigor)
    current_ndwi = Column(Float, nullable=True)  # NDWI (Moisture & Fire Hazard)
    cir_vigor_score = Column(Float, nullable=True)  # False Color Infrared Index
    sar_backscatter_vh_db = Column(Float, nullable=True)  # Sentinel-1 SAR Radar (dB)
    mean_canopy_height_m = Column(Float, nullable=True)  # 10m Canopy Height Model (CHM)
    biomass_tonnes_per_ha = Column(Float, nullable=True)  # Aboveground Biomass (t/ha)
    status = Column(String(50), default="Active", nullable=False)  # 'Active', 'Under Review', 'Degraded', 'Mature'
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    compartment = relationship("Compartment", back_populates="plantations")
    sample_plots = relationship("SamplePlot", back_populates="plantation", cascade="all, delete-orphan")
    carbon_reports = relationship("CarbonMRVReport", back_populates="plantation")


class SamplePlot(Base):
    __tablename__ = "sample_plots"

    id = Column(String(36), primary_key=True, default=default_uuid)
    plantation_id = Column(String(36), ForeignKey("plantations.id", ondelete="CASCADE"), nullable=False)
    plot_code = Column(String(100), unique=True, nullable=False, index=True)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_meters = Column(Float, default=17.84, nullable=False)
    area_ha = Column(Float, default=0.1, nullable=False)
    last_surveyed = Column(DateTime, nullable=True)
    survey_count = Column(Integer, default=0, nullable=False)
    assigned_guard_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="Active", nullable=False)  # 'Active', 'Pending Survey', 'Inactive'
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    plantation = relationship("Plantation", back_populates="sample_plots")
    assigned_guard = relationship("User", back_populates="assigned_plots", foreign_keys=[assigned_guard_id])
    tree_measurements = relationship("TreeMeasurement", back_populates="sample_plot", cascade="all, delete-orphan")


class TreeMeasurement(Base):
    __tablename__ = "tree_measurements"

    id = Column(String(36), primary_key=True, default=default_uuid)
    sample_plot_id = Column(String(36), ForeignKey("sample_plots.id", ondelete="CASCADE"), nullable=False)
    tree_number = Column(Integer, nullable=False)
    species_code = Column(String(50), nullable=False)
    species_local_name = Column(String(100), nullable=False)
    species_botanical_name = Column(String(150), nullable=False)
    gbh_cm = Column(Float, nullable=False)
    dbh_cm = Column(Float, nullable=False)
    height_m = Column(Float, nullable=False)
    health_status = Column(String(50), default="Healthy", nullable=False)  # 'Healthy', 'Diseased', 'Broken/Felled', 'Dead'
    recorded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    recorded_at = Column(DateTime, default=utc_now, nullable=False)
    notes = Column(String(500), nullable=True)

    # Relationships
    sample_plot = relationship("SamplePlot", back_populates="tree_measurements")
    recorder = relationship("User", foreign_keys=[recorded_by])

    @property
    def plot_code(self):
        return self.sample_plot.plot_code if self.sample_plot else None


class AlertIncident(Base):
    __tablename__ = "alert_incidents"

    id = Column(String(36), primary_key=True, default=default_uuid)
    compartment_id = Column(String(36), ForeignKey("compartments.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # 'Canopy Loss', 'Moisture Stress', 'Boundary Encroachment', 'Fire Risk', 'Illegal Felling'
    severity = Column(String(50), nullable=False)  # 'Critical', 'High', 'Medium', 'Low'
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    affected_area_ha = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    status = Column(String(50), default="Generated", nullable=False)  # 'Generated', 'Assigned', 'Under Inspection', 'Verified', 'Action Taken', 'Closed', 'False Alert'
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(1000), nullable=False)
    detected_at = Column(DateTime, default=utc_now, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    satellite_scene_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    compartment = relationship("Compartment", back_populates="alerts")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_alerts")
    creator_user = relationship("User", foreign_keys=[assigned_by], back_populates="created_alerts")
    field_inspections = relationship("FieldInspection", back_populates="alert", cascade="all, delete-orphan")


class FieldInspection(Base):
    __tablename__ = "field_inspections"

    id = Column(String(36), primary_key=True, default=default_uuid)
    alert_id = Column(String(36), ForeignKey("alert_incidents.id", ondelete="CASCADE"), nullable=False)
    officer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cause = Column(String(100), nullable=False)  # 'Illegal Felling', 'Natural Fall/Storm', 'Forest Fire', 'Riverbank Erosion', 'Grazing', 'False Alert', 'Other'
    verified_lat = Column(Float, nullable=False)
    verified_lng = Column(Float, nullable=False)
    photo_urls = Column(Text, default="[]", nullable=False)  # JSON array of URLs
    remarks = Column(Text, nullable=False)
    action_taken = Column(String(500), nullable=True)
    inspection_date = Column(DateTime, default=utc_now, nullable=False)
    synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    alert = relationship("AlertIncident", back_populates="field_inspections")
    officer = relationship("User", back_populates="field_inspections", foreign_keys=[officer_id])


class CarbonMRVReport(Base):
    __tablename__ = "carbon_mrv_reports"

    id = Column(String(36), primary_key=True, default=default_uuid)
    compartment_id = Column(String(36), ForeignKey("compartments.id", ondelete="SET NULL"), nullable=True)
    plantation_id = Column(String(36), ForeignKey("plantations.id", ondelete="SET NULL"), nullable=True)
    report_type = Column(String(50), nullable=False)  # 'Baseline', 'Monitoring', 'Verification'
    reporting_period_start = Column(DateTime, nullable=False)
    reporting_period_end = Column(DateTime, nullable=False)
    total_agb_tonnes = Column(Float, nullable=False)
    agb_per_ha = Column(Float, nullable=False)
    carbon_stock_tco2e = Column(Float, nullable=False)
    uncertainty_percent = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, nullable=False)
    confidence_interval_upper = Column(Float, nullable=False)
    methodology = Column(String(100), default="Verra VM0045", nullable=False)
    model_version = Column(String(50), nullable=False)
    satellite_scenes_used = Column(Text, default="[]", nullable=False)  # JSON array
    sample_plots_used = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=True)
    status = Column(String(50), default="Draft", nullable=False)  # 'Draft', 'Finalized', 'Audited', 'Certified'
    generated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    compartment = relationship("Compartment", back_populates="carbon_reports")
    plantation = relationship("Plantation", back_populates="carbon_reports")
    generator = relationship("User", back_populates="carbon_reports", foreign_keys=[generated_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=default_uuid)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'EXPORT', 'MODEL_RUN'
    changed_by = Column(String(255), nullable=False)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    description = Column(String(1000), nullable=False)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)


class SatelliteScene(Base):
    __tablename__ = "satellite_scenes"

    id = Column(String(36), primary_key=True, default=default_uuid)
    scene_id = Column(String(100), unique=True, nullable=False, index=True)
    satellite_name = Column(String(50), nullable=False, index=True)  # 'Sentinel-1 (SAR)', 'Sentinel-2 (MSI)', 'NASA GEDI (LiDAR)', 'PlanetScope (3m)'
    sensor_type = Column(String(100), nullable=False)  # 'C-Band SAR', 'Multispectral Optical', 'Spaceborne LiDAR', 'High-Res Optical'
    acquisition_date = Column(DateTime, nullable=False, index=True)
    cloud_cover_percent = Column(Float, default=0.0, nullable=False)
    resolution_meters = Column(Float, default=10.0, nullable=False)
    polarization_or_bands = Column(String(100), nullable=False)  # e.g. 'VV, VH, VV/VH', 'RGB, NIR, SWIR'
    orbit_pass = Column(String(30), default="Descending", nullable=False)  # 'Ascending', 'Descending'
    division_name = Column(String(100), default="All Divisions", nullable=False)
    centroid_lat = Column(Float, nullable=True)
    centroid_lng = Column(Float, nullable=True)
    area_ha = Column(Float, nullable=True)
    processing_level = Column(String(50), default="Level-2A", nullable=False)
    cloud_masked = Column(Boolean, default=False, nullable=False)
    fusion_status = Column(String(50), default="Raw Ingested", nullable=False)  # 'Raw Ingested', 'Calibrated', 'Cloud-Inpainted (SAR Fusion)', 'Biomass Inferred'
    footprint_geojson = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    ndvi_mean = Column(Float, nullable=True)  # NDVI (Vegetation Vigor)
    ndvi_change = Column(Float, nullable=True)
    ndwi_mean = Column(Float, nullable=True)  # NDWI (Canopy Moisture & Fire Hazard)
    cir_reflectance = Column(Float, nullable=True)  # False Color Infrared Ratio (NIR/Red)
    sar_backscatter_vv_db = Column(Float, nullable=True)
    sar_backscatter_vh_db = Column(Float, nullable=True)  # Sentinel-1 SAR VH (All-Weather Radar)
    sar_vh_vv_ratio = Column(Float, nullable=True)
    chm_mean_height_m = Column(Float, nullable=True)  # 10m Canopy Height Model (CHM)
    agb_density_t_ha = Column(Float, nullable=True)  # Aboveground Biomass Density (t/ha)
    cloud_penetration_verified = Column(Boolean, default=False, nullable=False)
    data_source = Column(String(300), default="Bhuvan NRSC / VEDAS SAC / Sentinel Hub", nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class CarbonCreditAssessment(Base):
    __tablename__ = "carbon_credit_assessments"

    id = Column(String(36), primary_key=True, default=default_uuid)
    assessment_id = Column(String(100), unique=True, nullable=False, index=True)
    division_name = Column(String(100), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    baseline_carbon_t = Column(Float, nullable=False)
    current_carbon_t = Column(Float, nullable=False)
    net_carbon_change_t = Column(Float, nullable=False)
    eligible_credits_tco2e = Column(Float, nullable=False)
    methodology = Column(String(200), default="IPCC 2006 Vol-4 AFOLU Tier-2 / Verra VM0045", nullable=False)
    standard = Column(String(100), default="Verra VCS", nullable=False)
    verifier_name = Column(String(200), default="Bureau Veritas India", nullable=False)
    serial_number = Column(String(200), nullable=True)
    status = Column(String(50), default="Verified", nullable=False)  # 'Draft', 'Submitted', 'Verified', 'Issued'
    sha256_hash = Column(String(64), nullable=True)
    data_source = Column(String(300), default="ISFR 2023 Baseline + Multi-Sensor MRV", nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class DroneSurvey(Base):
    __tablename__ = "drone_surveys"

    id = Column(String(36), primary_key=True, default=default_uuid)
    mission_code = Column(String(100), unique=True, nullable=False, index=True)
    survey_name = Column(String(255), nullable=False)
    division_name = Column(String(100), nullable=False, index=True)
    compartment_id = Column(String(36), ForeignKey("compartments.id", ondelete="SET NULL"), nullable=True)
    plantation_id = Column(String(36), ForeignKey("plantations.id", ondelete="SET NULL"), nullable=True)
    flight_date = Column(DateTime, nullable=False, index=True)
    uav_model = Column(String(100), default="DJI Matrice 350 RTK", nullable=False)
    sensor_type = Column(String(100), default="Multispectral RedEdge-P", nullable=False)  # 'Multispectral', 'RGB 45MP', 'UAV LiDAR', 'Thermal'
    flight_altitude_m = Column(Float, default=90.0, nullable=False)
    ground_sampling_distance_cm = Column(Float, default=2.5, nullable=False)  # GSD in cm/pixel
    covered_area_ha = Column(Float, default=45.0, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    flight_footprint_geojson = Column(Text, nullable=True)
    orthomosaic_url = Column(String(500), nullable=True)
    chm_url = Column(String(500), nullable=True)
    flight_log_url = Column(String(500), nullable=True)
    point_cloud_url = Column(String(500), nullable=True)
    boundary_file_url = Column(String(500), nullable=True)
    itc_crown_count = Column(Integer, default=0, nullable=False)  # AI-detected tree crowns / seedlings
    survival_rate_verified_pct = Column(Float, default=0.0, nullable=False)
    mean_canopy_height_m = Column(Float, default=4.5, nullable=False)  # 10m Canopy Height Model (CHM)
    biomass_estimate_t_ha = Column(Float, default=85.0, nullable=False)  # Aboveground Biomass (t/ha)
    mean_ndvi = Column(Float, default=0.82, nullable=True)  # NDVI (Vegetation Vigor)
    mean_ndwi = Column(Float, default=0.28, nullable=True)  # NDWI (Moisture & Fire Hazard)
    cir_reflectance = Column(Float, default=2.45, nullable=True)  # False Color Infrared Ratio
    sar_correlation_vh_db = Column(Float, default=-15.2, nullable=True)  # Sentinel-1 SAR VH Cross-Pol
    processing_status = Column(String(50), default="Raw Uploaded", nullable=False)  # 'Raw Uploaded', 'Orthomosaic Processed', 'AI Crown Segmented', 'MRV Calibrated'
    pilot_in_command = Column(String(150), default="ASSAC Drone Remote Sensing Unit", nullable=False)
    privacy_tier = Column(String(50), default="Department Confidential", nullable=False)  # 'Department Confidential', 'State Forestry MRV', 'Public Open'
    data_classification = Column(String(50), default="DGCA Compliant / Green Zone", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    compartment = relationship("Compartment", foreign_keys=[compartment_id])
    plantation = relationship("Plantation", foreign_keys=[plantation_id])


