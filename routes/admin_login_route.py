from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import AdminUser, User, Product, Type, Category, Department
from extensions import db
import os
import bcrypt
from werkzeug.utils import secure_filename
import requests

admin_login_bp = Blueprint('admin_login_bp', __name__)

UPLOAD_FOLDER = 'static/products'
ADMIN_FOLDER = 'static/admin'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

SUPABASE_URL = "https://bkdfuzkifmbyohpgdqgd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrZGZ1emtpZm1ieW9ocGdkcWdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjIzNDY5MCwiZXhwIjoyMDc3ODEwNjkwfQ.fMwa_6vxw1c0SXMzoLyDA6E0NKrLT0LUoXZtd8PnSds"

def upload_to_supabase(file, bucket):
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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ADMIN_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_login_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = AdminUser.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            session["user_type"] = "admin"  # ✅ Set user type
            login_user(admin, force=True)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_login_bp.admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('admin_login_bp.admin_login'))
    return render_template('admin_login.html')

@admin_login_bp.route('/admin-dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', admin=current_user)

@admin_login_bp.route('/admin-logout')
@login_required
def admin_logout():
    session.pop("user_type", None)  # ✅ Clear user type
    logout_user()
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login_bp.admin_login'))

@admin_login_bp.route('/edit-admin-profile', methods=['GET', 'POST'])
@login_required
def edit_admin_profile():
    admin = current_user
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        image_file = request.files.get('profile_image')

        if email:
            admin.email = email
        if username:
            admin.username = username
        if password:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            admin.password_hash = hashed_pw.decode('utf-8')
        if image_file and allowed_file(image_file.filename):
            image_url = upload_to_supabase(image_file, bucket="admin-images")
            if image_url:
                admin.profile_image = image_url

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin_login_bp.admin_dashboard'))

    return render_template('admin_edit_profile.html', admin=admin)


@admin_login_bp.route('/manage-customers')
@login_required
def manage_customers():
    customers = User.query.order_by(User.id.asc()).all()
    return render_template('admin_manage_customers.html', customers=customers, admin=current_user)

@admin_login_bp.route('/edit-customer/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(user_id):
    customer = User.query.get_or_404(user_id)
    if request.method == 'POST':
        customer.email = request.form['email']
        customer.username = request.form['username']
        customer.role = request.form['role']
        db.session.commit()
        flash('Customer updated successfully.', 'success')
        return redirect(url_for('admin_login_bp.manage_customers'))
    return render_template('admin_edit_customer.html', customer=customer, admin=current_user)

@admin_login_bp.route('/delete-customer/<int:user_id>', methods=['POST'])
@login_required
def delete_customer(user_id):
    customer = User.query.get_or_404(user_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully.', 'warning')
    return redirect(url_for('admin_login_bp.manage_customers'))

@admin_login_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    departments = Department.query.order_by(Department.name.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    types = Type.query.order_by(Type.name.asc()).all()

    if request.method == 'POST':
        last_product = Product.query.order_by(Product.id.desc()).first()
        next_number = (last_product.id + 1) if last_product else 1
        product_id = f"pdt{next_number:03d}"

        name = request.form['name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        department_name = request.form.get('department_name')
        category_name = request.form.get('category_name')
        type_name = request.form.get('type_name')
        image_file = request.files.get('image')

        if not department_name or not category_name or not type_name:
            flash('Department, Category, and Type are required.', 'danger')
            return redirect(request.url)

        department = Department.query.filter_by(name=department_name).first()
        if not department:
            department = Department(name=department_name)
            db.session.add(department)
            db.session.commit()
        department_id = department.id

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name, department_id=department_id)
            db.session.add(category)
            db.session.commit()
        category_id = category.id

        type_obj = Type.query.filter_by(name=type_name).first()
        if not type_obj:
            type_obj = Type(name=type_name, category_id=category_id, department_id=department_id)
            db.session.add(type_obj)
            db.session.commit()
        type_id = type_obj.id

        image_url = None
        if image_file and allowed_file(image_file.filename):
            image_url = upload_to_supabase(image_file, bucket="product-images")

        new_product = Product(
            product_id=product_id,
            name=name,
            price=price,
            quantity=quantity,
            image=image_url,
            type_id=type_id
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'Product {product_id} added successfully.', 'success')
        return redirect(url_for('admin_login_bp.add_product'))

    return render_template('admin_add_product.html', departments=departments, categories=categories, types=types, admin=current_user)
@admin_login_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    departments = Department.query.order_by(Department.name.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    types = Type.query.order_by(Type.name.asc()).all()

    if request.method == 'POST':
        print("Incoming edit request for product:", product_id)
        print("Form keys:", list(request.form.keys()))
        print("Form values:", request.form.to_dict())
        print("Files:", request.files)

        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.quantity = int(request.form['quantity'])

        department_name = request.form.get('department_name')
        category_name = request.form.get('category_name')
        type_name = request.form.get('type_name')

        print("Received department:", department_name)
        print("Received category:", category_name)
        print("Received type:", type_name)

        if not department_name or not category_name or not type_name:
            flash('Department, Category, and Type are required.', 'danger')
            return redirect(request.url)

        department = Department.query.filter_by(name=department_name).first()
        if not department:
            department = Department(name=department_name)
            db.session.add(department)
            db.session.commit()
        department_id = department.id

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name, department_id=department_id)
            db.session.add(category)
            db.session.commit()
        category_id = category.id

        type_obj = Type.query.filter_by(name=type_name).first()
        if not type_obj:
            type_obj = Type(name=type_name, category_id=category_id, department_id=department_id)
            db.session.add(type_obj)
            db.session.commit()

        print("Resolved type object:", type_obj)
        product.type_id = type_obj.id

        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            print("Image file received:", image_file.filename)
            image_url = upload_to_supabase(image_file, bucket="product-images")
            if image_url:
                product.image = image_url

        db.session.commit()
        print("Product updated successfully via edit route.")
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_login_bp.view_products'))

    return render_template('admin_edit_product.html', product=product, departments=departments, categories=categories, types=types, admin=current_user)

@admin_login_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'warning')
    return redirect(url_for('admin_login_bp.add_product'))

@admin_login_bp.route('/view-products')
@login_required
def view_products():
    products = Product.query.order_by(Product.id.desc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    types = Type.query.order_by(Type.name.asc()).all()
    return render_template('view_products.html', products=products, departments=departments, categories=categories, types=types, admin=current_user)

@admin_login_bp.route('/update-product/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    print("Incoming update request for product:", product_id)
    print("Form keys:", list(request.form.keys()))
    print("Form values:", request.form.to_dict())
    print("Files:", request.files)

    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    department_id = request.form.get('department_id')
    category_id = request.form.get('category_id')
    type_id = request.form.get('type_id')
    image_file = request.files.get('image')

    print("Received department_id:", department_id)
    print("Received category_id:", category_id)
    print("Received type_id:", type_id)

    if not department_id or not category_id or not type_id:
        print("Missing one or more IDs")
        return "Missing department, category, or type", 400

    if name:
        product.name = name
    if price:
        product.price = float(price)
    if quantity:
        product.quantity = int(quantity)

    try:
        department_id = int(department_id)
        category_id = int(category_id)
        type_id = int(type_id)
    except ValueError:
        print("Invalid ID format")
        return "Invalid ID format", 400

    department = Department.query.get(department_id)
    category = Category.query.get(category_id)
    type_obj = Type.query.get(type_id)

    print("Resolved department:", department)
    print("Resolved category:", category)
    print("Resolved type object:", type_obj)

    if not department or not category or not type_obj:
        print("Invalid department, category, or type ID")
        return "Invalid department, category, or type ID", 400

    product.type_id = type_obj.id

    if image_file and allowed_file(image_file.filename):
        print("Image file received:", image_file.filename)
        image_url = upload_to_supabase(image_file, bucket="product-images")
        if image_url:
            product.image = image_url

    db.session.commit()
    print("Product updated successfully via update route.")
    return '', 204