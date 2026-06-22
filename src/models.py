from datetime import datetime, timezone
from src.extensions import db
from flask_login import UserMixin

class Partner(UserMixin, db.Model):
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(150), nullable=True)
    password_last_changed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    vehicles = db.relationship('Vehicle', backref='partner', lazy=True)
    route_histories = db.relationship('RouteHistory', backref='partner', lazy=True)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    capacity_kg = db.Column(db.Float, nullable=False)
    fuel_efficiency_kml = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Active")
    
    route_histories = db.relationship('RouteHistory', backref='vehicle', lazy=True)

class RouteHistory(db.Model):
    __tablename__ = 'route_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    route_code = db.Column(db.String(50), unique=True, nullable=False)
    total_distance_km = db.Column(db.Float, nullable=False)
    estimated_fuel_cost = db.Column(db.Float, nullable=False)
    total_stops = db.Column(db.Integer, nullable=False)
    optimization_mode = db.Column(db.String(50), nullable=False) # e.g. 'Eco', 'Express', 'Balanced'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
