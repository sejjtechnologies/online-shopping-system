from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Product, Order
from extensions import db  # ✅ Fixed: import db from extensions, not app

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('login_bp.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login_bp.login'))
    return render_template('login.html')

@login_bp.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('dashboard.html', products=products)

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_bp.login'))

@login_bp.route('/customer-view-products')
def customer_view_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('customer_view_products.html', products=products)

@login_bp.route('/place-order', methods=['GET', 'POST'])
@login_required
def place_order():
    products = Product.query.order_by(Product.name.asc()).all()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])

        product = Product.query.get(product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('login_bp.place_order'))

        total = product.price * quantity

        new_order = Order(
            product_id=product.id,
            quantity=quantity,
            total_amount=total,
            user_id=current_user.id,
            user_email=current_user.email,
            user_username=current_user.username,
            status="Waiting"  # ✅ Default status
        )
        db.session.add(new_order)
        db.session.commit()
        flash(f'Order placed successfully! Total: Ugx {total:,.0f}', 'success')
        return redirect(url_for('login_bp.place_order'))

    return render_template('place_order.html', products=products)

@login_bp.route('/my-orders')
@login_required
def view_my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    return render_template('my_orders.html', orders=orders)

@login_bp.route('/view-cart')
def view_cart():
    # Placeholder logic — replace with actual cart retrieval
    cart_items = []  # Example: session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)

# ✅ Admin view of all customer orders
@login_bp.route('/admin/manage-orders')
@login_required
def manage_orders():
    orders = db.session.query(
        Order.id.label('order_id'),
        Product.name.label('product_name'),
        Order.quantity,
        Order.total_amount.label('total_price'),
        Order.timestamp.label('order_date'),
        Order.user_username.label('username'),
        Order.user_email.label('email'),
        Order.status
    ).join(Product, Order.product_id == Product.id).order_by(Order.timestamp.desc()).all()

    return render_template('admin_manage_orders.html', orders=orders)

# ✅ Admin toggle delivery status
@login_bp.route('/admin/mark-delivered/<int:order_id>', methods=['POST'])
@login_required
def mark_delivered(order_id):
    order = Order.query.get(order_id)
    if order:
        order.status = "Delivered" if order.status != "Delivered" else "Waiting"
        db.session.commit()
        flash(f"Order {order.id} marked as {order.status}.", "success")
    else:
        flash("Order not found.", "danger")
    return redirect(url_for('login_bp.manage_orders'))