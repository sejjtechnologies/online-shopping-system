from flask_login import UserMixin
from extensions import db
import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20))
    profile_image = db.Column(db.String(255), default='default.jpg')
    role = db.Column(db.String(20), default='customer')
    last_login = db.Column(db.DateTime)  # ✅ Added field

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except ValueError:
            return False

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(255), default='admin_default.jpg')
    role = db.Column(db.String(20), default='admin')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except ValueError:
            return False

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    categories = db.relationship('Category', backref='department', lazy=True)
    types = db.relationship('Type', back_populates='department', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    types = db.relationship('Type', back_populates='category', lazy=True)

class Type(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    category = db.relationship('Category', back_populates='types')
    department = db.relationship('Department', back_populates='types')
    products = db.relationship('Product', backref='type', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default="Waiting")

    product = db.relationship('Product', backref='orders')
    user = db.relationship('User', backref='orders')

class SystemWorker(db.Model, UserMixin):
    __tablename__ = 'system_workers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    profile_image = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except ValueError:
            return False

class SalesTransaction(db.Model):
    __tablename__ = 'sales_transactions'

    id = db.Column(db.Integer, primary_key=True)
    salesman_id = db.Column(db.Integer, db.ForeignKey('system_workers.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    salesman = db.relationship('SystemWorker', backref='sales_transactions')
    product = db.relationship('Product', backref='sales_transactions')

class SalesSession(db.Model):
    __tablename__ = 'sales_sessions'

    id = db.Column(db.Integer, primary_key=True)
    salesman_id = db.Column(db.Integer, db.ForeignKey('system_workers.id', ondelete='CASCADE'), nullable=False)
    session_start = db.Column(db.DateTime, default=db.func.current_timestamp())
    session_end = db.Column(db.DateTime, nullable=True)
    total_amount = db.Column(db.Numeric(14, 2), default=0)

    salesman = db.relationship('SystemWorker', backref='sales_sessions')

class SalesSummary(db.Model):
    __tablename__ = 'sales_summary'

    id = db.Column(db.Integer, primary_key=True)
    salesman_id = db.Column(db.Integer, db.ForeignKey('system_workers.id', ondelete='CASCADE'), unique=True, nullable=False)
    total_sales_amount = db.Column(db.Numeric(14, 2), default=0)
    total_products_sold = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

    salesman = db.relationship('SystemWorker', backref='sales_summary')

class LoginActivity(db.Model):
    __tablename__ = 'login_activity'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.Text)
    device_type = db.Column(db.String(50))
    device_name = db.Column(db.String(100))
    platform = db.Column(db.String(100))

    user = db.relationship('User', backref='login_activity')