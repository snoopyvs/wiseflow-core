import os
import sys

# Ensure the root directory is in the python path
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(basedir)

from src.app import app
from src.extensions import db
from src.models import Partner, Vehicle, RouteHistory
from datetime import datetime, timezone

def seed_data():
    with app.app_context():
        # Drop all tables and recreate them to ensure a clean state
        db.drop_all()
        db.create_all()

        print("Seeding database...")

        # 1. Create Partners (Akun Mitra)
        partner1 = Partner(
            username="mitra_satu",
            email="admin@mitrasatu.com",
            password_hash="hashed_password_123", # In a real app, use werkzeug.security
            company_name="PT Mitra Satu Logistik"
        )
        partner2 = Partner(
            username="mitra_dua",
            email="ops@mitradua.co.id",
            password_hash="hashed_password_456",
            company_name="CV Dua Armada Maju"
        )
        db.session.add_all([partner1, partner2])
        db.session.commit()

        # 2. Create Vehicles for Partner 1
        v1 = Vehicle(partner_id=partner1.id, plate_number="B 1234 CD", model="Volvo FH16", capacity_kg=24000, fuel_efficiency_kml=3.2)
        v2 = Vehicle(partner_id=partner1.id, plate_number="B 5678 EF", model="Scania R500", capacity_kg=22000, fuel_efficiency_kml=3.5)
        
        # 3. Create Vehicles for Partner 2
        v3 = Vehicle(partner_id=partner2.id, plate_number="D 9012 GH", model="Mitsubishi Fuso", capacity_kg=8000, fuel_efficiency_kml=5.1)
        v4 = Vehicle(partner_id=partner2.id, plate_number="D 3456 IJ", model="Hino Ranger", capacity_kg=12000, fuel_efficiency_kml=4.2)
        
        db.session.add_all([v1, v2, v3, v4])
        db.session.commit()

        # 4. Create Route Histories (Mock data generated after optimization)
        rh1 = RouteHistory(
            partner_id=partner1.id,
            vehicle_id=v1.id,
            route_code="RT-8924A",
            total_distance_km=142.5,
            estimated_fuel_cost=450000.0,
            total_stops=14,
            optimization_mode="Eco"
        )
        rh2 = RouteHistory(
            partner_id=partner1.id,
            vehicle_id=v2.id,
            route_code="RT-8923B",
            total_distance_km=85.2,
            estimated_fuel_cost=280000.0,
            total_stops=8,
            optimization_mode="Express"
        )
        rh3 = RouteHistory(
            partner_id=partner2.id,
            vehicle_id=v3.id,
            route_code="RT-9000X",
            total_distance_km=210.0,
            estimated_fuel_cost=600000.0,
            total_stops=22,
            optimization_mode="Balanced"
        )

        db.session.add_all([rh1, rh2, rh3])
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
