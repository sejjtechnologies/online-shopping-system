import psycopg2
from psycopg2 import sql

# Render PostgreSQL connection details
conn = psycopg2.connect(
    dbname="online_shopping_db_mnrn",
    user="online_shopping_db_mnrn_user",
    password="H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7",
    host="dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com",
    port="5432"
)

# Create a cursor
cur = conn.cursor()

# Define the SQL to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS system_workers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    profile_image TEXT,
    password TEXT NOT NULL
);
"""

# Execute and commit
cur.execute(create_table_query)
conn.commit()

print("✅ Table 'system_workers' created successfully.")

# Close connections
cur.close()
conn.close()