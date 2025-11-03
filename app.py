from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supermarket-secret-key'

# Import and initialize extensions
from extensions import db
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login_bp.admin_login'  # Redirect unauthorized users

@login_manager.user_loader
def load_user(user_id):
    from models import User, AdminUser  # Delayed import to avoid circular reference
    return db.session.get(AdminUser, int(user_id)) or db.session.get(User, int(user_id))

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

# Home route renders home.html
@app.route('/')
def home():
    return render_template('home.html')

# Bind to Render's assigned port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)