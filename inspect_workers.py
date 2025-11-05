import psycopg2

# Connection details from Render
conn = psycopg2.connect(
    host="dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com",
    port=5432,
    dbname="online_shopping_db_mnrn",
    user="online_shopping_db_mnrn_user",
    password="H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7",
    sslmode="require"
)

try:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM system_workers;")
        rows = cur.fetchall()
        print("\n--- system_workers ---")
        for row in rows:
            print(row)
finally:
    conn.close()