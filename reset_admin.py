from extensions import db
from models import AdminUser
from app import app  # ensures app context is available

# Admin credentials
email = "sejjtechnologies@gmail.com"
username = "sejjtechnologies"
password = "sejjtech"

with app.app_context():
    # Delete existing admin if found
    existing = AdminUser.query.filter_by(email=email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print("🗑️ Existing admin user deleted.")

    # Create new admin with bcrypt password
    new_admin = AdminUser(
        email=email,
        username=username,
        role="admin",
        profile_image="admin_default.jpg"
    )
    new_admin.set_password(password)

    db.session.add(new_admin)
    db.session.commit()
    print("✅ New admin user inserted successfully.")