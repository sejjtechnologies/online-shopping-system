from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import bcrypt

# Database URL for your Render Postgres
DATABASE_URL = "postgresql+psycopg://online_shopping_db_mnrn_user:H30CdH5oCDnz7EBV3bLdjd6IYE3C5pk7@dpg-d44ja015pdvs739o88bg-a.oregon-postgres.render.com:5432/online_shopping_db_mnrn"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define the AdminUser model (match your table structure)
class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False)
    username = Column(String(80), nullable=False)
    password_hash = Column(String(256), nullable=False)
    profile_image = Column(String(255))
    role = Column(String(20))

# User details
email = "sejjtechnologies@gmail.com"
username = "sejjtech"
password = "sejjtech"  # plaintext password
role = "Admin"

# Hash the password with bcrypt
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create the admin user instance
admin_user = AdminUser(
    email=email,
    username=username,
    password_hash=hashed_password,
    role=role
)

# Insert into database
try:
    session.add(admin_user)
    session.commit()
    print("✅ Admin user inserted successfully!")
except Exception as e:
    session.rollback()
    print("❌ Failed to insert admin user:", e)
finally:
    session.close()
