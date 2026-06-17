import os
from flask import Flask, render_template, redirect, url_for
from src.extensions import db
from src.models import Partner, Vehicle, RouteHistory

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

if __name__ == '__main__':
    # Menjalankan server Flask dalam mode debug
    app.run(debug=True, port=5000)
