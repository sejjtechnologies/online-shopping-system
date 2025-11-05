import psycopg2
import bcrypt

# Render PostgreSQL connection details (from your Flask config)
DB_URL = "postgresql://online_shopping_db_mnrn_user:H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/online_shopping_db_mnrn"

# Worker details
username = "Salesman"
email = "salesman@gmail.com"
role = "Salesman"
plain_password = "salesman"

# Hash the password using bcrypt
hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Insert into system_workers table
try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    insert_query = """
        INSERT INTO system_workers (username, email, role, password)
        VALUES (%s, %s, %s, %s)
    """
    cur.execute(insert_query, (username, email, role, hashed_password))
    conn.commit()

    print("✅ Salesman worker inserted successfully.")

except Exception as e:
    print(f"❌ Error inserting worker: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()