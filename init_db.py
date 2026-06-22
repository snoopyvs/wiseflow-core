from src.app import app
from src.extensions import db
from src.models import Partner
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    
    # Create default user
    print("Creating default user...")
    hashed_password = generate_password_hash("admin123")
    default_partner = Partner(
        username="admin",
        email="admin@wiseflow.com",
        password_hash=hashed_password,
        company_name="Apex Logistics Global",
        password_last_changed=datetime.now(timezone.utc)
    )
    db.session.add(default_partner)
    db.session.commit()
    print("Database initialized successfully!")
