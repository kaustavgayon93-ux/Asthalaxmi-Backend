import sqlite3

conn = sqlite3.connect('asthalaxmi.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(satellite_scenes);')
cols = [row[1] for row in cursor.fetchall()]
print('Existing cols in satellite_scenes:', cols)

new_cols = [
    ('ndvi_mean', 'REAL'),
    ('ndvi_change', 'REAL'),
    ('sar_backscatter_vv_db', 'REAL'),
    ('sar_backscatter_vh_db', 'REAL'),
    ('sar_vh_vv_ratio', 'REAL'),
    ('cloud_penetration_verified', 'BOOLEAN DEFAULT 0'),
    ('data_source', 'VARCHAR(300) DEFAULT "Bhuvan NRSC / VEDAS SAC / Sentinel Hub"')
]

for col_name, col_type in new_cols:
    if col_name not in cols:
        print(f'Adding column {col_name} {col_type}...')
        cursor.execute(f'ALTER TABLE satellite_scenes ADD COLUMN {col_name} {col_type};')

conn.commit()
conn.close()
print('Migration complete!')
