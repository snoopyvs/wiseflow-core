import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from src.extensions import db
from src.models import Partner, Vehicle, RouteHistory
from src.ai_optimizer import solve_routing
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-dev-secret-key-12345')

# Configure Database
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'wiseflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Partner.query.get(int(user_id))

@app.route('/')
def index():
    # Redirect ke dashboard secara default
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    vehicles_count = Vehicle.query.filter_by(partner_id=current_user.id).count()
    recent_routes = RouteHistory.query.filter_by(partner_id=current_user.id).order_by(RouteHistory.created_at.desc()).limit(3).all()
    total_routes = RouteHistory.query.filter_by(partner_id=current_user.id).count()
    return render_template('dashboard.html', vehicles_count=vehicles_count, recent_routes=recent_routes, total_routes=total_routes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        user = Partner.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({"message": "Logged in successfully", "redirect": url_for('dashboard')})
        return jsonify({"error": "Invalid email or password"}), 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        company_name = data.get('company_name')
        email = data.get('email')
        password = data.get('password')
        
        if Partner.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
            
        hashed_password = generate_password_hash(password)
        username = "".join(e for e in company_name if e.isalnum()).lower()
        import random
        while Partner.query.filter_by(username=username).first():
            username += str(random.randint(0, 9))
            
        new_partner = Partner(
            username=username,
            email=email,
            password_hash=hashed_password,
            company_name=company_name,
            password_last_changed=datetime.datetime.now(datetime.timezone.utc)
        )
        db.session.add(new_partner)
        db.session.commit()
        login_user(new_partner)
        return jsonify({"message": "Registered successfully", "redirect": url_for('dashboard')})
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/master-data')
@login_required
def master_data():
    vehicles = Vehicle.query.filter_by(partner_id=current_user.id).all()
    return render_template('master_data.html', vehicles=vehicles)

@app.route('/optimizer')
@login_required
def optimizer():
    vehicles = Vehicle.query.filter_by(partner_id=current_user.id).all()
    return render_template('optimizer.html', vehicles=vehicles)

@app.route('/history')
@login_required
def history():
    history_logs = RouteHistory.query.filter_by(partner_id=current_user.id).order_by(RouteHistory.created_at.desc()).all()
    return render_template('history.html', history_logs=history_logs)

@app.route('/settings')
@login_required
def settings():
    vehicles = Vehicle.query.filter_by(partner_id=current_user.id).all()
    return render_template('settings.html', vehicles=vehicles)

@app.route('/api/settings/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    password = data.get('password')
    if not check_password_hash(current_user.password_hash, password):
        return jsonify({"error": "Invalid current password"}), 401
    
    current_user.company_name = data.get('company_name', current_user.company_name)
    current_user.email = data.get('email', current_user.email)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})

@app.route('/api/settings/password', methods=['PUT'])
@login_required
def update_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({"error": "Invalid current password"}), 401
        
    # Check 1-day cooldown
    if current_user.password_last_changed:
        time_since_change = datetime.datetime.now(datetime.timezone.utc) - current_user.password_last_changed.replace(tzinfo=datetime.timezone.utc)
        if time_since_change.total_seconds() < 86400: # 24 hours
            return jsonify({"error": "You can only change your password once every 24 hours."}), 403
            
    current_user.password_hash = generate_password_hash(new_password)
    current_user.password_last_changed = datetime.datetime.now(datetime.timezone.utc)
    db.session.commit()
    return jsonify({"message": "Password changed successfully"})

@app.route('/api/vehicles', methods=['POST'])
@login_required
def add_vehicle():
    data = request.json
    partner = current_user
    if not partner:
        return jsonify({"error": "No partner found"}), 400
    
    new_vehicle = Vehicle(
        partner_id=partner.id,
        plate_number=data.get('plate_number'),
        model=data.get('model'),
        capacity_kg=float(data.get('capacity_kg', 0)),
        fuel_efficiency_kml=float(data.get('fuel_efficiency_kml', 0)),
        status="Active"
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle added successfully", "id": new_vehicle.id})

@app.route('/api/vehicles/<int:id>', methods=['PUT'])
@login_required
def update_vehicle(id):
    data = request.json
    vehicle = Vehicle.query.filter_by(id=id, partner_id=current_user.id).first_or_404()
    
    vehicle.plate_number = data.get('plate_number', vehicle.plate_number)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.capacity_kg = float(data.get('capacity_kg', vehicle.capacity_kg))
    vehicle.fuel_efficiency_kml = float(data.get('fuel_efficiency_kml', vehicle.fuel_efficiency_kml))
    
    db.session.commit()
    return jsonify({"message": "Vehicle updated successfully"})

@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
@login_required
def delete_vehicle(id):
    vehicle = Vehicle.query.filter_by(id=id, partner_id=current_user.id).first_or_404()
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted successfully"})

@app.route('/api/optimize', methods=['POST'])
@login_required
def api_optimize():
    data = request.json
    start_point = data.get('start_point')
    destinations = data.get('destinations', [])
    vehicle_id = data.get('vehicle_id')
    mode = data.get('mode', 'balanced')
    
    if not start_point or not destinations:
        return jsonify({"error": "Start point and destinations are required"}), 400
        
    partner = current_user
    vehicle = Vehicle.query.filter_by(id=vehicle_id, partner_id=current_user.id).first() if vehicle_id else None
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found. Please select a valid vehicle."}), 404
        
    # Validasi Kapasitas Ekstrim (Barang satuan melebihi kapasitas truk)
    for dest in destinations:
        if float(dest.get('demand', 0)) > vehicle.capacity_kg:
            return jsonify({"error": f"Barang untuk {dest.get('name')} ({dest.get('demand')}kg) melebihi kapasitas maksimal truk ({vehicle.capacity_kg}kg)."}), 400
            
    # Combine start point and destinations into one list for the algorithm
    locations = [start_point] + destinations
    
    # Run algorithms for comparison
    result_astar = solve_routing(locations, vehicle.capacity_kg, vehicle.fuel_efficiency_kml, use_heuristic=True, mode=mode.capitalize())
    result_dijkstra = solve_routing(locations, vehicle.capacity_kg, vehicle.fuel_efficiency_kml, use_heuristic=False, mode=mode.capitalize())
    
    # Save to database
    if partner and vehicle:
        # Generate a random route code like RT-8924A
        date_str = datetime.datetime.now().strftime("%y%m%d")
        route_code = f"ADM-ORD-{date_str}-{str(uuid.uuid4())[:4].upper()}"
        
        fuel_cost = result_astar.get('total_fuel_cost_rp', 0)
        
        history = RouteHistory(
            partner_id=partner.id,
            vehicle_id=vehicle.id,
            route_code=route_code,
            total_distance_km=result_astar['total_distance_km'],
            estimated_fuel_cost=fuel_cost,
            total_stops=len(destinations),
            optimization_mode=mode.capitalize()
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify({
        "astar": result_astar,
        "dijkstra": result_dijkstra
    })

if __name__ == '__main__':
    # Menjalankan server Flask dalam mode debug
    app.run(debug=True, host='0.0.0.0', port=5001)
