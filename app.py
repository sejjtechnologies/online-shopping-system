from flask import Flask, render_template, request, redirect, session, flash
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import requests
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# ✅ Timezone and relative time filter setup
from pytz import timezone
from datetime import datetime

UGANDA_TZ = timezone("Africa/Kampala")

def relative_time(value):
    now = datetime.utcnow()
    diff = now - value
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"

app.jinja_env.filters['relative_time'] = relative_time
app.jinja_env.globals['UGANDA_TZ'] = UGANDA_TZ

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg://online_shopping_db_mnrn_user:"
    "H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@"
    "dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/"
    "online_shopping_db_mnrn"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "supermarket-secret-key")

# Supabase credentials
SUPABASE_URL = "https://bkdfuzkifmbyohpgdqgd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrZGZ1emtpZm1ieW9ocGdkcWdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjIzNDY5MCwiZXhwIjoyMDc3ODEwNjkwfQ.fMwa_6vxw1c0SXMzoLyDA6E0NKrLT0LUoXZtd8PnSds"

def upload_to_supabase(file, bucket="admin-images"):
    try:
        filename = secure_filename(file.filename)
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": file.content_type
        }

        response = requests.put(upload_url, headers=headers, data=file.read())
        if response.ok:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        else:
            print(f"❌ Supabase upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during Supabase upload: {e}")
        return None

# Import and initialize SQLAlchemy
from extensions import db
db.init_app(app)

# Safe commit wrapper
def safe_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Database commit failed: {e}")
        flash("Something went wrong while saving. Please try again.", "danger")

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_bp.login"

@login_manager.user_loader
def load_user(user_id):
    from models import User, AdminUser
    user_type = session.get("user_type")
    if user_type == "admin":
        return db.session.get(AdminUser, int(user_id))
    return db.session.get(User, int(user_id))

# Register blueprints
from routes.login import login_bp
from routes.register import register_bp
from routes.admin_login_route import admin_login_bp
from routes.admin_worker_route import admin_worker_bp
from routes.staff_routes import staff_routes

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(admin_login_bp)
app.register_blueprint(admin_worker_bp)
app.register_blueprint(staff_routes)

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except SQLAlchemyError as e:
        print(f"❌ Error creating tables: {e}")

# Home route with staff roles
@app.route("/")
def home():
    from models import SystemWorker
    try:
        roles = db.session.query(SystemWorker.role).distinct().all()
        staff_roles = [r[0] for r in roles if r[0]]
    except SQLAlchemyError as e:
        print(f"❌ Error loading staff roles: {e}")
        staff_roles = []
    return render_template("home.html", staff_roles=staff_roles)

# About Us route
@app.route("/about")
def about():
    return render_template("about.html")

# Contact Us route
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Health check route for Render
@app.route("/health")
def health():
    return "OK", 200

# Start the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Starting app on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)