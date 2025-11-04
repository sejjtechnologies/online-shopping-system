from sqlalchemy import create_engine, inspect

# Render External Database URL
DATABASE_URL = "postgresql+psycopg://online_shopping_db_mnrn_user:H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/online_shopping_db_mnrn"

try:
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create inspector to list tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if tables:
        print("✅ Tables in the database:")
        for table in tables:
            print(f"- {table}")
    else:
        print("⚠️ No tables found in the database.")

except Exception as e:
    print("❌ Connection or query failed:", e)
