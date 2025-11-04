from flask import Flask
from extensions import db
from sqlalchemy import text  # ✅ Import text wrapper

# Initialize Flask app
app = Flask(__name__)

# Render PostgreSQL connection string
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg://online_shopping_db_mnrn_user:"
    "H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@"
    "dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/"
    "online_shopping_db_mnrn"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# Run ALTER TABLE inside app context
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'Waiting'"))
        db.session.commit()
        print("✅ 'status' column added to orders table on Render.")
    except Exception as e:
        print("❌ Failed to add column:", e)