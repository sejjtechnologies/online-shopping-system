from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from extensions import db
import requests

admin_worker_bp = Blueprint("admin_worker_bp", __name__)

# Supabase config
SUPABASE_URL = "https://bkdfuzkifmbyohpgdqgd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrZGZ1emtpZm1ieW9ocGdkcWdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjIzNDY5MCwiZXhwIjoyMDc3ODEwNjkwfQ.fMwa_6vxw1c0SXMzoLyDA6E0NKrLT0LUoXZtd8PnSds"

def upload_to_supabase(file, bucket="admin-images"):
    filename = secure_filename(file.filename)
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": file.content_type,
    }

    response = requests.put(upload_url, headers=headers, data=file.read())
    if response.ok:
        return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    return None

@admin_worker_bp.route("/create-worker", methods=["GET", "POST"])
def create_worker():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        image = request.files.get("profile_image")

        image_url = upload_to_supabase(image) if image else None
        hashed_password = generate_password_hash(password)

        insert_query = """
            INSERT INTO system_workers (username, email, role, profile_image, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            db.session.execute(insert_query, (username, email, role, image_url, hashed_password))
            db.session.commit()
            flash("✅ Worker created successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error: {str(e)}", "danger")

        return redirect(url_for("admin_login_bp.admin_dashboard"))

    return render_template("admin_create_worker.html")

@admin_worker_bp.route("/manage-roles")
def manage_roles():
    try:
        result = db.session.execute("SELECT * FROM system_workers")
        workers = result.fetchall()
    except Exception as e:
        flash(f"❌ Failed to load roles: {str(e)}", "danger")
        workers = []

    return render_template("admin_manage_roles.html", workers=workers)