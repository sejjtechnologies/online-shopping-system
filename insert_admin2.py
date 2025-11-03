from extensions import db
from models import AdminUser
from app import app
import bcrypt

# Define admin credentials
email = "admin@gmail.com"
username = "admin1"
password = "admin123"
role = "admin"
profile_image = "admin_default.jpg"

# Hash the password using bcrypt
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create admin user instance
admin = AdminUser(
    email=email,
    username=username,
    password_hash=hashed_password,
    role=role,
    profile_image=profile_image
)

# Insert into database
with app.app_context():
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user 'admin1' inserted successfully.")