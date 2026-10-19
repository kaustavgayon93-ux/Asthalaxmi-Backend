import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('asthalaxmi.db')
c = conn.cursor()

# 1. Add columns to divisions
existing_div_cols = [col[1] for col in c.execute('PRAGMA table_info(divisions)').fetchall()]
cols_to_add = [
    ('vdf_area_ha', 'FLOAT DEFAULT 0.0'),
    ('mdf_area_ha', 'FLOAT DEFAULT 0.0'),
    ('of_area_ha', 'FLOAT DEFAULT 0.0'),
    ('carbon_stock_mt', 'FLOAT DEFAULT 0.0'),
    ('boundary_source', "VARCHAR(255) DEFAULT 'Survey of India OSM 1:50K / FSI ISFR 2023'"),
    ('headquarters', 'VARCHAR(100)')
]
for col_name, col_type in cols_to_add:
    if col_name not in existing_div_cols:
        c.execute(f'ALTER TABLE divisions ADD COLUMN {col_name} {col_type}')
        print(f'Added column {col_name} to divisions')

# 2. Add columns to drone_surveys
existing_drone_cols = [col[1] for col in c.execute('PRAGMA table_info(drone_surveys)').fetchall()]
drone_cols_to_add = [
    ('flight_log_url', 'VARCHAR(500)'),
    ('point_cloud_url', 'VARCHAR(500)'),
    ('boundary_file_url', 'VARCHAR(500)')
]
for col_name, col_type in drone_cols_to_add:
    if col_name not in existing_drone_cols:
        c.execute(f'ALTER TABLE drone_surveys ADD COLUMN {col_name} {col_type}')
        print(f'Added column {col_name} to drone_surveys')

conn.commit()

# Clean up any bad test rows
c.execute("DELETE FROM divisions WHERE code = 'hhh'")
conn.commit()

# 3. Seed 16 Official Divisions
now_iso = datetime.now(timezone.utc).isoformat()
divisions_16 = [
    ('div-kamrup-01', 'Kamrup East Division', 'KAM-E', 'Lower Assam Circle', 'Assam', 68450.0, 42.8, 5, 4110.0, 14500.0, 10700.0, 6.8, 'Guwahati'),
    ('div-kamrup-w-02', 'Kamrup West Division', 'KAM-W', 'Lower Assam Circle', 'Assam', 95200.0, 48.5, 6, 6800.0, 22100.0, 17300.0, 9.4, 'Boko'),
    ('div-nagaon-04', 'Nagaon Division', 'NAG-S', 'Central Assam Circle', 'Assam', 72100.0, 34.6, 5, 3200.0, 12400.0, 9350.0, 7.1, 'Nagaon'),
    ('div-sonitpur-02', 'Sonitpur Division', 'SON-W', 'Northern Assam Circle', 'Assam', 88400.0, 41.2, 5, 5400.0, 18600.0, 12400.0, 8.7, 'Tezpur'),
    ('div-golaghat-03', 'Golaghat Division', 'GOL-01', 'Eastern Assam Circle', 'Assam', 79800.0, 51.2, 6, 7200.0, 21400.0, 12250.0, 8.9, 'Golaghat'),
    ('div-jorhat-06', 'Jorhat Division', 'JOR-01', 'Upper Assam Circle', 'Assam', 58300.0, 31.4, 4, 2100.0, 9800.0, 6400.0, 5.6, 'Jorhat'),
    ('div-dibrugarh-07', 'Dibrugarh Division', 'DIB-01', 'Upper Assam Circle', 'Assam', 66200.0, 37.8, 4, 3800.0, 13200.0, 8000.0, 6.9, 'Dibrugarh'),
    ('div-tinsukia-08', 'Tinsukia Division', 'TIN-01', 'Upper Assam Circle', 'Assam', 112500.0, 54.3, 7, 14200.0, 28600.0, 18300.0, 14.8, 'Tinsukia'),
    ('div-cachar-09', 'Cachar Division', 'CAC-01', 'Southern Assam (Barak Valley) Circle', 'Assam', 84700.0, 46.1, 5, 5900.0, 19800.0, 13300.0, 9.1, 'Silchar'),
    ('div-karbi-10', 'Karbi Anglong East Division', 'KAE-01', 'Autonomous Hill Districts Circle', 'Assam', 215000.0, 78.4, 8, 36185.0, 82400.0, 50000.0, 31.2, 'Diphu'),
    ('div-kokrajhar-11', 'Kokrajhar Division', 'KOK-01', 'Bodoland Territorial Region Circle', 'Assam', 92300.0, 52.6, 6, 8500.0, 24100.0, 16000.0, 10.3, 'Kokrajhar'),
    ('div-goalpara-12', 'Goalpara Division', 'GOA-01', 'Western Assam Circle', 'Assam', 61400.0, 39.8, 4, 3600.0, 12800.0, 8000.0, 6.2, 'Goalpara'),
    ('div-dimahasao-13', 'Dima Hasao Division', 'DIH-01', 'Autonomous Hill Districts Circle', 'Assam', 198000.0, 82.1, 7, 49979.0, 74200.0, 38400.0, 33.5, 'Haflong'),
    ('div-bongaigaon-14', 'Bongaigaon Division', 'BON-01', 'Western Assam Circle', 'Assam', 44600.0, 28.9, 3, 1800.0, 6900.0, 4200.0, 4.1, 'Bongaigaon'),
    ('div-kaziranga-15', 'Kaziranga National Park Division', 'KAZ-NP', 'Wildlife Wing Circle', 'Assam', 108400.0, 66.8, 5, 18400.0, 34200.0, 19800.0, 16.5, 'Bokakhat'),
    ('div-manas-16', 'Manas National Park Division', 'MAN-NP', 'Wildlife Wing Circle', 'Assam', 95000.0, 71.5, 4, 15200.0, 32800.0, 19900.0, 14.1, 'Barpeta Road')
]

for d in divisions_16:
    c.execute('''
        INSERT INTO divisions (id, name, code, circle_name, state, total_area_ha, forest_cover_percent, num_ranges, vdf_area_ha, mdf_area_ha, of_area_ha, carbon_stock_mt, headquarters, boundary_source, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Survey of India OSM 1:50K / FSI ISFR 2023', ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            name=excluded.name,
            circle_name=excluded.circle_name,
            total_area_ha=excluded.total_area_ha,
            forest_cover_percent=excluded.forest_cover_percent,
            num_ranges=excluded.num_ranges,
            vdf_area_ha=excluded.vdf_area_ha,
            mdf_area_ha=excluded.mdf_area_ha,
            of_area_ha=excluded.of_area_ha,
            carbon_stock_mt=excluded.carbon_stock_mt,
            headquarters=excluded.headquarters,
            updated_at=excluded.updated_at
    ''', (d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], d[11], d[12], now_iso, now_iso))

conn.commit()
count = c.execute('SELECT COUNT(*) FROM divisions').fetchone()[0]
print(f'Total divisions in DB: {count}')
all_divs = c.execute('SELECT code, name, circle_name, forest_cover_percent, carbon_stock_mt FROM divisions').fetchall()
for div in all_divs:
    print('  -', div)
conn.close()
