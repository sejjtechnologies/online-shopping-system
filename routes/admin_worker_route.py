from flask import Blueprint, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from extensions import db
from sqlalchemy import text
import requests
import bcrypt

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

# ---------------- Create Worker ----------------
@admin_worker_bp.route("/create-worker", methods=["GET", "POST"])
def create_worker():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        image = request.files.get("profile_image")

        image_url = upload_to_supabase(image) if image else None
        # Hash password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        insert_query = text("""
            INSERT INTO system_workers (username, email, role, profile_image, password)
            VALUES (:username, :email, :role, :profile_image, :password)
        """)
        try:
            db.session.execute(insert_query, {
                "username": username,
                "email": email,
                "role": role,
                "profile_image": image_url,
                "password": hashed_password
            })
            db.session.commit()
            flash("✅ Worker created successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error: {str(e)}", "danger")

        return redirect(url_for("admin_worker_bp.manage_roles"))

    return render_template("admin_create_worker.html")

# ---------------- Manage Roles ----------------
@admin_worker_bp.route("/manage-roles")
def manage_roles():
    try:
        result = db.session.execute(text("SELECT * FROM system_workers"))
        workers = result.fetchall()
    except Exception as e:
        flash(f"❌ Failed to load roles: {str(e)}", "danger")
        workers = []

    return render_template("admin_manage_roles.html", workers=workers)

# ---------------- Edit Worker ----------------
@admin_worker_bp.route("/edit-worker/<int:worker_id>", methods=["GET", "POST"])
def edit_worker(worker_id):
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")
        image = request.files.get("profile_image")

        image_url = upload_to_supabase(image) if image else None

        update_query = text("""
            UPDATE system_workers
            SET username = :username,
                email = :email,
                role = :role,
                profile_image = COALESCE(:profile_image, profile_image)
            WHERE id = :worker_id
        """)
        try:
            db.session.execute(update_query, {
                "username": username,
                "email": email,
                "role": role,
                "profile_image": image_url,
                "worker_id": worker_id
            })

            if password:
                # Hash new password with bcrypt
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.execute(text("""
                    UPDATE system_workers SET password = :password WHERE id = :worker_id
                """), {
                    "password": hashed_password,
                    "worker_id": worker_id
                })

            db.session.commit()
            flash("✅ Worker updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error updating worker: {str(e)}", "danger")

        return redirect(url_for("admin_worker_bp.manage_roles"))

    # GET: Load worker data
    try:
        result = db.session.execute(text("SELECT * FROM system_workers WHERE id = :worker_id"), {"worker_id": worker_id})
        worker = result.fetchone()
        if not worker:
            flash("❌ Worker not found.", "danger")
            return redirect(url_for("admin_worker_bp.manage_roles"))
    except Exception as e:
        flash(f"❌ Error loading worker: {str(e)}", "danger")
        return redirect(url_for("admin_worker_bp.manage_roles"))

    return render_template("admin_edit_worker.html", worker=worker)

# ---------------- Delete Worker ----------------
@admin_worker_bp.route("/delete-worker/<int:worker_id>")
def delete_worker(worker_id):
    try:
        db.session.execute(text("DELETE FROM system_workers WHERE id = :worker_id"), {"worker_id": worker_id})
        db.session.commit()
        flash("✅ Worker deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error deleting worker: {str(e)}", "danger")

    return redirect(url_for("admin_worker_bp.manage_roles"))
