import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from src.extensions import db
from src.models import Partner, Vehicle, RouteHistory
from src.ai_optimizer import solve_routing
import uuid

app = Flask(__name__)

# Configure Database
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'wiseflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

@app.route('/')
def index():
    # Redirect ke dashboard secara default
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/master-data')
def master_data():
    vehicles = Vehicle.query.all()
    return render_template('master_data.html', vehicles=vehicles)

@app.route('/optimizer')
def optimizer():
    vehicles = Vehicle.query.all()
    return render_template('optimizer.html', vehicles=vehicles)

@app.route('/history')
def history():
    history_logs = RouteHistory.query.order_by(RouteHistory.created_at.desc()).all()
    return render_template('history.html', history_logs=history_logs)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    partner = Partner.query.first() # Using mock partner
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
def update_vehicle(id):
    data = request.json
    vehicle = Vehicle.query.get_or_404(id)
    
    vehicle.plate_number = data.get('plate_number', vehicle.plate_number)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.capacity_kg = float(data.get('capacity_kg', vehicle.capacity_kg))
    vehicle.fuel_efficiency_kml = float(data.get('fuel_efficiency_kml', vehicle.fuel_efficiency_kml))
    
    db.session.commit()
    return jsonify({"message": "Vehicle updated successfully"})

@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted successfully"})

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    data = request.json
    start_point = data.get('start_point')
    destinations = data.get('destinations', [])
    vehicle_id = data.get('vehicle_id')
    mode = data.get('mode', 'balanced')
    
    if not start_point or not destinations:
        return jsonify({"error": "Start point and destinations are required"}), 400
        
    # Combine start point and destinations into one list for the algorithm
    locations = [start_point] + destinations
    
    # Run algorithms for comparison
    result_astar = solve_routing(locations, use_heuristic=True, mode=mode.capitalize())
    result_dijkstra = solve_routing(locations, use_heuristic=False, mode=mode.capitalize())
    
    # Save to database
    partner = Partner.query.first()
    vehicle = Vehicle.query.get(vehicle_id) if vehicle_id else None
    
    if partner and vehicle:
        # Generate a random route code like RT-8924A
        route_code = f"RT-{str(uuid.uuid4())[:6].upper()}"
        
        fuel_liters = result_astar['total_distance_km'] / vehicle.fuel_efficiency_kml if vehicle.fuel_efficiency_kml else 0
        fuel_cost = fuel_liters * 6800 # Mock fuel price: Rp 6.800 / Liter (Subsidized Solar)
        
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
