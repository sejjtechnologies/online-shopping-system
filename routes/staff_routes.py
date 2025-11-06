from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from models import db, SystemWorker, Product, SalesTransaction, SalesSummary
import bcrypt
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict

staff_routes = Blueprint("staff_routes", __name__)


@staff_routes.route("/staff-login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        worker = SystemWorker.query.filter_by(email=email).first()

        if worker and bcrypt.checkpw(
            password.encode("utf-8"), worker.password.encode("utf-8")
        ):
            session["staff_id"] = worker.id
            session["staff_name"] = worker.username
            session["staff_role"] = worker.role
            flash("Login successful", "success")

            if worker.role.strip().lower() == "salesman":
                return redirect(url_for("staff_routes.sales_dashboard"))
            else:
                return redirect(url_for("staff_routes.staff_dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("staff_routes.staff_login"))

    return render_template("staff_login.html")


@staff_routes.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("staff_routes.reset_password"))

        worker = SystemWorker.query.filter_by(email=email).first()
        if not worker:
            flash("No account found with that email", "warning")
            return redirect(url_for("staff_routes.reset_password"))

        hashed_pw = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        worker.password = hashed_pw
        db.session.commit()

        flash("Password reset successfully. You can now log in.", "success")
        return redirect(url_for("staff_routes.staff_login"))

    return render_template("reset_your_own_password.html")


@staff_routes.route("/staff-dashboard")
def staff_dashboard():
    if "staff_id" not in session:
        flash("Please log in first", "warning")
        return redirect(url_for("staff_routes.staff_login"))

    return render_template("staff_dashboard.html", staff_name=session.get("staff_name"))


@staff_routes.route("/sales-dashboard")
def sales_dashboard():
    if (
        "staff_id" not in session
        or session.get("staff_role", "").strip().lower() != "salesman"
    ):
        flash("Unauthorized access", "danger")
        return redirect(url_for("staff_routes.staff_login"))

    selected_date = session.get("selected_sales_date")
    if not selected_date:
        selected_date = date.today().isoformat()
        session["selected_sales_date"] = selected_date

    salesman_id = session["staff_id"]
    start = datetime.strptime(selected_date, "%Y-%m-%d")
    end = datetime.combine(start.date(), datetime.max.time())

    transactions = SalesTransaction.query.filter(
        SalesTransaction.salesman_id == salesman_id,
        SalesTransaction.timestamp >= start,
        SalesTransaction.timestamp <= end
    ).all()

    todays_sales = sum(t.unit_price * t.quantity_sold for t in transactions)

    return render_template(
        "sales_dashboard.html",
        staff_name=session.get("staff_name"),
        selected_date=selected_date,
        todays_sales=todays_sales
    )


@staff_routes.route("/set-sales-date", methods=["POST"])
def set_sales_date():
    selected_date = request.form.get("sales_date")
    session["selected_sales_date"] = selected_date
    flash(f"Sales date set to {selected_date}", "info")
    return redirect(url_for("staff_routes.sales_dashboard"))


@staff_routes.route("/sales-view-products")
def sales_view_products():
    if (
        "staff_id" not in session
        or session.get("staff_role", "").strip().lower() != "salesman"
    ):
        flash("Unauthorized access", "danger")
        return redirect(url_for("staff_routes.staff_login"))

    products = Product.query.order_by(Product.id.asc()).all()
    return render_template("sales_view_products.html", products=products)


@staff_routes.route("/start-selling")
def start_selling():
    if (
        "staff_id" not in session
        or session.get("staff_role", "").strip().lower() != "salesman"
    ):
        flash("Unauthorized access", "danger")
        return redirect(url_for("staff_routes.staff_login"))

    products = Product.query.order_by(Product.name.asc()).all()
    return render_template("start_selling.html", products=products)


@staff_routes.route("/submit-sale", methods=["POST"])
def submit_sale():
    if (
        "staff_id" not in session
        or session.get("staff_role", "").strip().lower() != "salesman"
    ):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json()
    items = data.get("items", [])
    salesman_id = session["staff_id"]

    total_sale_amount = Decimal("0.00")
    total_products_sold = 0

    for item in items:
        product_id = int(item.get("productId"))
        quantity = int(item.get("quantity"))
        price = Decimal(str(item.get("price")))

        product = db.session.get(Product, product_id)
        if not product or product.quantity < quantity:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Insufficient stock for {product.name}",
                    }
                ),
                400,
            )

        transaction = SalesTransaction(
            salesman_id=salesman_id,
            product_id=product_id,
            quantity_sold=quantity,
            unit_price=price,
            timestamp=datetime.now(),
        )
        db.session.add(transaction)

        product.quantity -= quantity
        total_sale_amount += price * quantity
        total_products_sold += quantity

    summary = SalesSummary.query.filter_by(salesman_id=salesman_id).first()
    if summary:
        summary.total_sales_amount += total_sale_amount
        summary.total_products_sold += total_products_sold
        summary.last_updated = datetime.now()
    else:
        summary = SalesSummary(
            salesman_id=salesman_id,
            total_sales_amount=total_sale_amount,
            total_products_sold=total_products_sold,
            last_updated=datetime.now(),
        )
        db.session.add(summary)

    db.session.commit()
    return jsonify({"status": "success", "message": "Sale recorded successfully"})


@staff_routes.route("/sales-summary")
def sales_summary():
    transactions = SalesTransaction.query.join(Product).order_by(SalesTransaction.timestamp.asc()).all()

    daily_sales = defaultdict(list)
    chart_labels = []
    chart_data = []

    totals_by_date = defaultdict(Decimal)

    for t in transactions:
        day = t.timestamp.date()
        daily_sales[day].append(t)
        totals_by_date[day] += t.unit_price * t.quantity_sold

    sorted_days = sorted(totals_by_date.keys())
    for day in sorted_days:
        chart_labels.append(day.strftime("%d/%m/%Y"))
        chart_data.append(float(totals_by_date[day]))

    return render_template(
        "sales_summary.html",
        daily_sales=daily_sales,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


@staff_routes.route("/staff-logout")
def staff_logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("staff_routes.staff_login"))