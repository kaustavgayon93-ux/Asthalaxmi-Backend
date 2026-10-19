import sqlite3
import random

conn = sqlite3.connect('asthalaxmi.db')
cursor = conn.cursor()

def add_col_if_missing(table, col_name, col_type):
    cursor.execute(f"PRAGMA table_info({table});")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if col_name not in existing_cols:
        print(f"Adding {col_name} ({col_type}) to {table}...")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};")

# 1. Compartments
add_col_if_missing("compartments", "mean_ndvi", "REAL")
add_col_if_missing("compartments", "mean_ndwi", "REAL")
add_col_if_missing("compartments", "cir_index", "REAL")
add_col_if_missing("compartments", "sar_vh_backscatter_db", "REAL")
add_col_if_missing("compartments", "canopy_height_m", "REAL")
add_col_if_missing("compartments", "biomass_tonnes_per_ha", "REAL")

# 2. Plantations
add_col_if_missing("plantations", "current_ndwi", "REAL")
add_col_if_missing("plantations", "cir_vigor_score", "REAL")
add_col_if_missing("plantations", "sar_backscatter_vh_db", "REAL")
add_col_if_missing("plantations", "mean_canopy_height_m", "REAL")

# 3. Satellite Scenes
add_col_if_missing("satellite_scenes", "ndwi_mean", "REAL")
add_col_if_missing("satellite_scenes", "cir_reflectance", "REAL")
add_col_if_missing("satellite_scenes", "chm_mean_height_m", "REAL")
add_col_if_missing("satellite_scenes", "agb_density_t_ha", "REAL")

# 4. Drone Surveys
add_col_if_missing("drone_surveys", "mean_ndvi", "REAL")
add_col_if_missing("drone_surveys", "mean_ndwi", "REAL")
add_col_if_missing("drone_surveys", "cir_reflectance", "REAL")
add_col_if_missing("drone_surveys", "sar_correlation_vh_db", "REAL")

conn.commit()

# Populate Compartments with calibrated multi-sensor metrics
print("\nEnriching Compartments with multi-sensor spectral & radar metrics...")
cursor.execute("SELECT id, forest_type, canopy_density_percent FROM compartments;")
rows = cursor.fetchall()
for comp_id, f_type, canopy in rows:
    f_type = f_type or ""
    if "Wet Evergreen" in f_type:
        ndvi = round(random.uniform(0.83, 0.89), 2)
        ndwi = round(random.uniform(0.32, 0.44), 2)
        cir = round(random.uniform(2.95, 3.40), 2)
        sar_vh = round(random.uniform(-13.5, -11.5), 1)
        chm = round(random.uniform(25.0, 32.0), 1)
        agb = round(random.uniform(240.0, 310.0), 1)
    elif "Semi-Evergreen" in f_type:
        ndvi = round(random.uniform(0.78, 0.84), 2)
        ndwi = round(random.uniform(0.26, 0.36), 2)
        cir = round(random.uniform(2.65, 3.00), 2)
        sar_vh = round(random.uniform(-15.0, -13.0), 1)
        chm = round(random.uniform(20.0, 26.5), 1)
        agb = round(random.uniform(190.0, 250.0), 1)
    elif "Moist Deciduous" in f_type:
        ndvi = round(random.uniform(0.72, 0.79), 2)
        ndwi = round(random.uniform(0.18, 0.28), 2)
        cir = round(random.uniform(2.40, 2.75), 2)
        sar_vh = round(random.uniform(-16.8, -14.5), 1)
        chm = round(random.uniform(17.0, 23.0), 1)
        agb = round(random.uniform(155.0, 210.0), 1)
    elif "Bamboo" in f_type:
        ndvi = round(random.uniform(0.70, 0.77), 2)
        ndwi = round(random.uniform(0.22, 0.32), 2)
        cir = round(random.uniform(2.25, 2.55), 2)
        sar_vh = round(random.uniform(-17.5, -15.5), 1)
        chm = round(random.uniform(11.0, 15.5), 1)
        agb = round(random.uniform(95.0, 135.0), 1)
    else:  # Grassland / Alluvial
        ndvi = round(random.uniform(0.64, 0.72), 2)
        ndwi = round(random.uniform(0.35, 0.48), 2)
        cir = round(random.uniform(1.95, 2.25), 2)
        sar_vh = round(random.uniform(-20.5, -18.0), 1)
        chm = round(random.uniform(4.5, 8.5), 1)
        agb = round(random.uniform(50.0, 85.0), 1)

    cursor.execute("""
        UPDATE compartments 
        SET mean_ndvi = ?, mean_ndwi = ?, cir_index = ?, sar_vh_backscatter_db = ?, canopy_height_m = ?, biomass_tonnes_per_ha = ?
        WHERE id = ?;
    """, (ndvi, ndwi, cir, sar_vh, chm, agb, comp_id))

print(f"Updated {len(rows)} compartments.")

# Populate Plantations
print("\nEnriching Plantations with multi-sensor spectral & radar metrics...")
cursor.execute("SELECT id, primary_species, planting_year, area_ha FROM plantations;")
rows = cursor.fetchall()
for plt_id, species, yr, area in rows:
    species = species or ""
    age = max(1, 2026 - (yr or 2022))
    
    if "Teak" in species:
        ndvi = round(min(0.88, 0.65 + age * 0.035), 2)
        ndwi = round(0.12 + age * 0.02, 2)
        cir = round(2.1 + age * 0.15, 2)
        sar_vh = round(-18.5 + age * 0.7, 1)
        chm = round(min(22.0, 4.0 + age * 2.2), 1)
        agb = round(min(210.0, 35.0 + age * 18.0), 1)
    elif "Sal" in species:
        ndvi = round(min(0.89, 0.68 + age * 0.03), 2)
        ndwi = round(0.18 + age * 0.02, 2)
        cir = round(2.3 + age * 0.14, 2)
        sar_vh = round(-17.5 + age * 0.65, 1)
        chm = round(min(24.0, 4.5 + age * 2.0), 1)
        agb = round(min(235.0, 42.0 + age * 21.0), 1)
    elif "Bamboo" in species:
        ndvi = round(min(0.82, 0.62 + age * 0.04), 2)
        ndwi = round(0.24 + age * 0.015, 2)
        cir = round(2.0 + age * 0.12, 2)
        sar_vh = round(-19.0 + age * 0.6, 1)
        chm = round(min(16.0, 3.5 + age * 2.5), 1)
        agb = round(min(145.0, 30.0 + age * 16.0), 1)
    elif "Rubber" in species:
        ndvi = round(min(0.85, 0.67 + age * 0.035), 2)
        ndwi = round(0.19 + age * 0.02, 2)
        cir = round(2.2 + age * 0.14, 2)
        sar_vh = round(-17.8 + age * 0.65, 1)
        chm = round(min(18.0, 3.8 + age * 2.1), 1)
        agb = round(min(165.0, 32.0 + age * 17.5), 1)
    elif "Hollong" in species:
        ndvi = round(min(0.90, 0.70 + age * 0.035), 2)
        ndwi = round(0.25 + age * 0.025, 2)
        cir = round(2.4 + age * 0.16, 2)
        sar_vh = round(-16.5 + age * 0.7, 1)
        chm = round(min(26.0, 5.0 + age * 2.4), 1)
        agb = round(min(260.0, 48.0 + age * 24.0), 1)
    else:  # Sissoo / Mixed
        ndvi = round(min(0.84, 0.64 + age * 0.03), 2)
        ndwi = round(0.16 + age * 0.018, 2)
        cir = round(2.1 + age * 0.13, 2)
        sar_vh = round(-18.0 + age * 0.6, 1)
        chm = round(min(19.0, 3.8 + age * 1.9), 1)
        agb = round(min(150.0, 30.0 + age * 15.0), 1)

    cursor.execute("""
        UPDATE plantations 
        SET current_ndvi = ?, current_ndwi = ?, cir_vigor_score = ?, sar_backscatter_vh_db = ?, mean_canopy_height_m = ?, biomass_tonnes_per_ha = ?
        WHERE id = ?;
    """, (ndvi, ndwi, cir, sar_vh, chm, agb, plt_id))

print(f"Updated {len(rows)} plantations.")

# Populate Satellite Scenes
print("\nEnriching Satellite Scenes with multi-sensor spectral & radar metrics...")
cursor.execute("SELECT id, satellite_name, sensor_type FROM satellite_scenes;")
rows = cursor.fetchall()
for sc_id, sat_name, s_type in rows:
    is_sar = "SAR" in (s_type or "") or "Sentinel-1" in (sat_name or "") or "RISAT" in (sat_name or "")
    if is_sar:
        ndvi = None
        ndwi = None
        cir = None
        sar_vv = round(random.uniform(-13.0, -9.5), 1)
        sar_vh = round(random.uniform(-19.5, -14.0), 1)
        ratio = round(pow(10, (sar_vh - sar_vv) / 10.0), 3)
        chm = round(random.uniform(18.0, 28.0), 1)
        agb = round(random.uniform(165.0, 260.0), 1)
        pen = 1
    else:
        ndvi = round(random.uniform(0.72, 0.88), 2)
        ndwi = round(random.uniform(0.18, 0.38), 2)
        cir = round(random.uniform(2.4, 3.2), 2)
        sar_vv = None
        sar_vh = None
        ratio = None
        chm = round(random.uniform(16.0, 26.0), 1)
        agb = round(random.uniform(145.0, 240.0), 1)
        pen = 0

    cursor.execute("""
        UPDATE satellite_scenes 
        SET ndvi_mean = ?, ndwi_mean = ?, cir_reflectance = ?, sar_backscatter_vv_db = ?, sar_backscatter_vh_db = ?, sar_vh_vv_ratio = ?, chm_mean_height_m = ?, agb_density_t_ha = ?, cloud_penetration_verified = ?
        WHERE id = ?;
    """, (ndvi, ndwi, cir, sar_vv, sar_vh, ratio, chm, agb, pen, sc_id))

print(f"Updated {len(rows)} satellite scenes.")

# Populate Drone Surveys
print("\nEnriching Drone Surveys with multi-sensor spectral & radar metrics...")
cursor.execute("SELECT id, covered_area_ha, sensor_type FROM drone_surveys;")
rows = cursor.fetchall()
for dr_id, area, s_type in rows:
    ndvi = round(random.uniform(0.81, 0.89), 2)
    ndwi = round(random.uniform(0.24, 0.36), 2)
    cir = round(random.uniform(2.70, 3.15), 2)
    sar_vh = round(random.uniform(-15.8, -13.2), 1)
    chm = round(random.uniform(5.5, 14.5), 1)
    agb = round(random.uniform(85.0, 160.0), 1)

    cursor.execute("""
        UPDATE drone_surveys 
        SET mean_ndvi = ?, mean_ndwi = ?, cir_reflectance = ?, sar_correlation_vh_db = ?, mean_canopy_height_m = ?, biomass_estimate_t_ha = ?
        WHERE id = ?;
    """, (ndvi, ndwi, cir, sar_vh, chm, agb, dr_id))

print(f"Updated {len(rows)} drone surveys.")

conn.commit()
conn.close()
print("\nMulti-sensor spectral & radar enrichment completed successfully!")
