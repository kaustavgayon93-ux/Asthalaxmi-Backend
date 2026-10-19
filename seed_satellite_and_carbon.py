import sys
from datetime import datetime, timezone, timedelta
import random
import hashlib

from database import engine, Base, SessionLocal
from models import SatelliteScene, CarbonCreditAssessment, Division

# Re-create any missing tables like carbon_credit_assessments
Base.metadata.create_all(bind=engine)

db = SessionLocal()

divisions = [d.name for d in db.query(Division).all()]
if not divisions:
    divisions = ["Kamrup East Division", "Sonitpur East Division", "Golaghat Division", "Nagaon Division"]

sc_count = db.query(SatelliteScene).count()
print(f"Current satellite scenes in DB: {sc_count}")

# Seed if empty or update existing with SAR/Optical data
sensors = [
    ("Sentinel-2 (MSI)", "Multispectral Optical", "B02, B03, B04, B08, B11, B12", 10.0, False, "Bhuvan NRSC / ESA Copernicus"),
    ("Sentinel-1 (SAR)", "C-Band Synthetic Aperture Radar", "VV, VH, VV/VH", 10.0, True, "NASA ASF / ESA Copernicus SAR"),
    ("RISAT-2B (ISRO)", "X-Band Synthetic Aperture Radar", "Circular Polarimetric (RH, RV)", 3.0, True, "ISRO VEDAS / SAC"),
    ("PlanetScope", "High-Res Optical", "RGB, NIR (4-Band)", 3.0, False, "NIC SI-Platform / Planet NICFI"),
    ("Landsat-9 (OLI-2/TIRS-2)", "Multispectral & Thermal", "Coastal, RGB, NIR, SWIR, Thermal", 30.0, False, "USGS EarthExplorer"),
]

if sc_count < 15:
    print("Seeding 25 multi-sensor satellite scenes...")
    for i in range(25):
        sat_name, s_type, bands, res, is_sar, src = random.choice(sensors)
        div = random.choice(divisions)
        dt = datetime(2025, random.randint(1, 12), random.randint(1, 28), tzinfo=timezone.utc)
        cloud = 0.0 if is_sar else (round(random.uniform(35.0, 85.0), 1) if dt.month in [6, 7, 8] else round(random.uniform(2.0, 25.0), 1))
        
        vv = round(random.uniform(-13.5, -9.0), 2) if is_sar else None
        vh = round(random.uniform(-21.0, -14.5), 2) if is_sar else None
        ratio = round(pow(10, (vh - vv) / 10.0), 3) if is_sar else None
        ndvi = None if is_sar else round(random.uniform(0.62, 0.88), 3)
        ndvi_chg = None if is_sar else round(random.uniform(-0.04, 0.05), 3)

        sc = SatelliteScene(
            scene_id=f"SCN-2025-{sat_name[:3].upper()}-{i+101:03d}",
            satellite_name=sat_name,
            sensor_type=s_type,
            acquisition_date=dt,
            cloud_cover_percent=cloud,
            resolution_meters=res,
            polarization_or_bands=bands,
            orbit_pass="Descending" if i % 2 == 0 else "Ascending",
            division_name=div,
            processing_level="Level-2A (Surface Reflectance / Radiometrically Calibrated)",
            cloud_masked=not is_sar,
            fusion_status="SAR-Cloud Penetrated" if is_sar else "Optical Atmospheric Corrected",
            ndvi_mean=ndvi,
            ndvi_change=ndvi_chg,
            sar_backscatter_vv_db=vv,
            sar_backscatter_vh_db=vh,
            sar_vh_vv_ratio=ratio,
            cloud_penetration_verified=is_sar,
            data_source=src,
        )
        db.add(sc)
    db.commit()
    print("Seeded 25 satellite scenes successfully.")

cc_count = db.query(CarbonCreditAssessment).count()
print(f"Current carbon credit assessments in DB: {cc_count}")

if cc_count < 6:
    print("Seeding Carbon Credit Assessments with traceability...")
    standards = ["Verra VCS", "Gold Standard", "Plan Vivo", "UNFCCC Article 6.4"]
    verifiers = ["Bureau Veritas India", "TÜV SÜD South Asia", "EPIC Sustainability Services"]

    for i, div in enumerate(divisions[:12]):
        baseline = round(random.uniform(420000, 910000), 2)
        net_c = round(random.uniform(14000, 52000), 2)
        current = baseline + net_c
        credits = round(net_c * 3.67, 2)
        std = random.choice(standards)
        vfr = random.choice(verifiers)

        h = hashlib.sha256(f"CRD-AS-2025-{i+1:03d}:{div}:{credits}:{std}".encode()).hexdigest()

        cc = CarbonCreditAssessment(
            assessment_id=f"CRD-AS-2025-{i+101:03d}",
            division_name=div,
            period_start=datetime(2023, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2025, 12, 31, tzinfo=timezone.utc),
            baseline_carbon_t=baseline,
            current_carbon_t=current,
            net_carbon_change_t=net_c,
            eligible_credits_tco2e=credits,
            methodology="IPCC 2006 Vol-4 AFOLU Tier-2 / Verra VM0045 ARR",
            standard=std,
            verifier_name=vfr,
            serial_number=f"IN-ASM-{std[:3].upper()}-2025-{i+1:04d}-{random.randint(10000, 99999)}",
            status="Verified" if i % 2 == 0 else "Audited",
            sha256_hash=h,
            data_source="FSI ISFR 2023 Baseline + Multi-Sensor MRV (Sentinel-1/2)",
        )
        db.add(cc)
    db.commit()
    print("Seeded 12 carbon credit assessments successfully.")

db.close()
print("Done seeding satellite and carbon credit data.")
