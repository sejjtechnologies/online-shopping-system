from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://online_shopping_db_mnrn_user:H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/online_shopping_db_mnrn"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connection successful:", result.scalar())
except Exception as e:
    print("❌ Connection failed:", e)
