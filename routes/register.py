from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from models import User
from extensions import db
import bcrypt
import datetime

register_bp = Blueprint("register_bp", __name__)


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        phone_number = request.form["phone_number"]
        password = request.form["password"]
        role = request.form.get("role", "customer")

        if (
            User.query.filter_by(email=email).first()
            or User.query.filter_by(username=username).first()
        ):
            flash("Email or username already exists", "danger")
            return redirect(url_for("register_bp.register"))

        new_user = User(
            email=email,
            username=username,
            phone_number=phone_number,
            role=role,
            profile_image="default.jpg",
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("register.html")


@register_bp.route("/account-settings")
@login_required
def account_settings():
    return render_template("customer_account_settings.html")


@register_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone_number"]
    image = request.files.get("profile_image")

    current_user.username = name
    current_user.email = email
    current_user.phone_number = phone

    if image and image.filename:
        from app import upload_to_supabase

        image_url = upload_to_supabase(image, bucket="customer-images")
        if image_url:
            current_user.profile_image = image_url

    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("register_bp.account_settings"))


@register_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("register_bp.account_settings"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "warning")
        return redirect(url_for("register_bp.account_settings"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("register_bp.account_settings"))


@register_bp.route("/logout-all-sessions", methods=["POST"])
@login_required
def logout_all_sessions():
    logout_user()
    session.clear()
    flash("You have been logged out from all devices.", "info")
    return redirect(url_for("login_bp.login"))


@register_bp.route("/view-login-activity")
@login_required
def view_login_activity():
    # Placeholder: implement actual tracking later
    activity = [
        {
            "timestamp": datetime.datetime.utcnow(),
            "ip": request.remote_addr,
            "device": "Current Device",
        },
    ]
    return render_template("login_activity.html", activity=activity)
