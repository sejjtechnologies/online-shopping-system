from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from models import User, SalesTransaction, Product, SystemWorker, Type, Category
from extensions import db
import bcrypt
import datetime
from sqlalchemy import func

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
    from models import LoginActivity

    logs = LoginActivity.query.filter_by(user_id=current_user.id).order_by(LoginActivity.timestamp.desc()).all()
    latest = logs[0] if logs else None

    print("📋 Total login records:", len(logs))
    print("🕒 Latest login activity timestamp:", latest.timestamp if latest else "None")

    return render_template("login_activity.html", activity=logs, latest=latest)

@register_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        print("🔧 Password reset attempt")
        print("📧 Email entered:", email)
        print("🔑 New password:", new_password)
        print("🔁 Confirm password:", confirm_password)

        user = User.query.filter_by(email=email).first()
        print("👤 User found:", user.username if user else "None")

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("register_bp.reset_password"))

        if new_password != confirm_password:
            print("❌ Passwords do not match")
            flash("Passwords do not match.", "warning")
            return redirect(url_for("register_bp.reset_password"))

        user.set_password(new_password)
        db.session.commit()
        print("✅ Password reset successful for:", user.username)

        flash("Password reset successful. You can now log in.", "success")
        return redirect(url_for("login_bp.login"))

    return render_template("customer_reset_password.html")

@register_bp.route("/admin/view-account-balance")
@login_required
def view_account_balance():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = db.session.query(SalesTransaction).join(Product).join(SystemWorker)

        if start_date:
            query = query.filter(SalesTransaction.timestamp >= start_date)
        if end_date:
            query = query.filter(SalesTransaction.timestamp <= end_date)

        # Breakdown by salesman
        salesman_breakdown = db.session.query(
            SystemWorker.username,
            func.sum(SalesTransaction.quantity_sold).label("total_quantity"),
            func.sum(SalesTransaction.quantity_sold * SalesTransaction.unit_price).label("total_revenue")
        ).join(SalesTransaction).group_by(SystemWorker.username).all()

        # Breakdown by product category (via Product → Type → Category)
        category_breakdown = db.session.query(
            Category.name,
            func.sum(SalesTransaction.quantity_sold).label("total_quantity"),
            func.sum(SalesTransaction.quantity_sold * SalesTransaction.unit_price).label("total_revenue")
        ).join(SalesTransaction.product).join(Product.type).join(Type.category).group_by(Category.name).all()

        # Overall totals
        total_quantity = query.with_entities(func.coalesce(func.sum(SalesTransaction.quantity_sold), 0)).scalar()
        total_revenue = query.with_entities(func.coalesce(func.sum(SalesTransaction.quantity_sold * SalesTransaction.unit_price), 0)).scalar()

        return render_template("admin_view_account_balance.html",
                               total_quantity=total_quantity,
                               total_revenue=total_revenue,
                               salesman_breakdown=salesman_breakdown,
                               category_breakdown=category_breakdown,
                               start_date=start_date,
                               end_date=end_date)
    except Exception as e:
        print(f"❌ Error calculating sales breakdown: {e}")
        return render_template("admin_view_account_balance.html",
                               total_quantity=0,
                               total_revenue=0,
                               salesman_breakdown=[],
                               category_breakdown=[],
                               start_date=None,
                               end_date=None)