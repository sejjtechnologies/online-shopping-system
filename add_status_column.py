from extensions import db
from models import Order
from app import app

with app.app_context():
    # Check if column already exists (optional safeguard)
    if not hasattr(Order, 'status'):
        db.session.execute('ALTER TABLE "order" ADD COLUMN status VARCHAR(20) DEFAULT \'Waiting\'')
        db.session.commit()
        print("✅ 'status' column added to Order table.")
    else:
        print("⚠️ 'status' column already exists.")