from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import requests
from werkzeug.utils import secure_filename

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure database
# Using Render PostgreSQL connection string directly
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg://online_shopping_db_mnrn_user:"
    "H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@"
    "dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/"
    "online_shopping_db_mnrn"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "supermarket-secret-key")

# Supabase credentials (hardcoded for now)
SUPABASE_URL = "https://bkdfuzkifmbyohpgdqgd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrZGZ1emtpZm1ieW9ocGdkcWdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjIzNDY5MCwiZXhwIjoyMDc3ODEwNjkwfQ.fMwa_6vxw1c0SXMzoLyDA6E0NKrLT0LUoXZtd8PnSds"

def upload_to_supabase(file, bucket="admin-images"):
    filename = secure_filename(file.filename)
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": file.content_type
    }

    response = requests.put(upload_url, headers=headers, data=file.read())
    if response.ok:
        return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    return None

# Import and initialize SQLAlchemy
from extensions import db
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_bp.login"  # ✅ Redirect unauthorized users to customer login

@login_manager.user_loader
def load_user(user_id):
    # Delayed import to avoid circular dependencies
    from models import User, AdminUser

    user_type = session.get("user_type")
    if user_type == "admin":
        return db.session.get(AdminUser, int(user_id))
    return db.session.get(User, int(user_id))

# Register blueprints
from routes.login import login_bp
from routes.register import register_bp
from routes.admin_login_route import admin_login_bp

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(admin_login_bp)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Home route
@app.route("/")
def home():
    return render_template("home.html")

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