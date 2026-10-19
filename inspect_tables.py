import sqlite3

conn = sqlite3.connect('asthalaxmi.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

for t in sorted(tables):
    if t.startswith('sqlite_'):
        continue
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [f"{row[1]} ({row[2]})" for row in cursor.fetchall()]
    cursor.execute(f"SELECT count(*) FROM {t};")
    cnt = cursor.fetchone()[0]
    print(f"\n==============================")
    print(f"Table: {t} | Rows: {cnt}")
    print(f"Columns: {', '.join(cols)}")
    
    # Show sample row
    if cnt > 0:
        cursor.execute(f"SELECT * FROM {t} LIMIT 1;")
        sample = cursor.fetchone()
        col_names = [c.split(' ')[0] for c in cols]
        print("Sample row:")
        for col_name, val in zip(col_names[:8], sample[:8]):
            print(f"  {col_name}: {val}")
        if len(col_names) > 8:
            print(f"  ... ({len(col_names) - 8} more columns)")

conn.close()
