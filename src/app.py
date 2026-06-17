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
    return render_template('master_data.html')

@app.route('/optimizer')
def optimizer():
    return render_template('optimizer.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    data = request.json
    start_point = data.get('start_point')
    destinations = data.get('destinations', [])
    mode = data.get('mode', 'balanced')
    
    if not start_point or not destinations:
        return jsonify({"error": "Start point and destinations are required"}), 400
        
    # Combine start point and destinations into one list for the algorithm
    locations = [start_point] + destinations
    
    # Run algorithms for comparison
    result_astar = solve_routing(locations, use_heuristic=True, mode=mode.capitalize())
    result_dijkstra = solve_routing(locations, use_heuristic=False, mode=mode.capitalize())
    
    # Save to database (using dummy vehicle and partner for now)
    # We pick the first partner and vehicle from our seed data
    partner = Partner.query.first()
    vehicle = Vehicle.query.first()
    
    if partner and vehicle:
        # Generate a random route code like RT-8924A
        route_code = f"RT-{str(uuid.uuid4())[:6].upper()}"
        
        history = RouteHistory(
            partner_id=partner.id,
            vehicle_id=vehicle.id,
            route_code=route_code,
            total_distance_km=result_astar['total_distance_km'],
            estimated_fuel_cost=result_astar['total_distance_km'] * 15000, # Mock fuel cost calculation
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
    app.run(debug=True, port=5000)
