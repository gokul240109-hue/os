from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from log_parser import load_logs
from db_manager import insert_logs, fetch_logs
from pattern_mining import mine_patterns
from prediction import model_predict, train_model_simple
from auth import register_user, authenticate_user, get_user_by_username
import pandas as pd
import traceback
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'os-log-analysis-secret-key-123')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Train model on startup
def init_model():
    try:
        logs = load_logs()
        if not logs.empty and 'level' in logs.columns and 'message' in logs.columns:
            if train_model_simple(logs):
                print("✓ ML Model trained successfully!")
            else:
                print("⚠ Could not train ML model, will use keyword-based predictions")
        else:
            print("⚠ Insufficient data to train model, will use keyword-based predictions")
    except Exception as e:
        print(f"Note: {e}")

# Initialize model when app starts
init_model()

# Create demo account on startup
def create_demo_account():
    try:
        user = get_user_by_username('admin')
        if not user:
            success, msg = register_user('admin', 'admin123', 'admin@example.com', 'Admin')
            if success:
                print("✓ Demo account created: admin / admin123")
    except Exception as e:
        print(f"Note: Demo account - {e}")

create_demo_account()

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        success, user_data, message = authenticate_user(username, password)
        
        if success:
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['email'] = user_data['email']
            session['role'] = user_data['role']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=message)
    
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    return render_template('login.html')

# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'Viewer')
        
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        if len(username) < 3 or len(username) > 20:
            return render_template('register.html', error='Username must be 3-20 characters')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return render_template('register.html', error='Password must contain uppercase, lowercase, and numbers')
        
        success, message = register_user(username, password, email, role)
        
        if success:
            return render_template('register.html', success=message)
        else:
            return render_template('register.html', error=message)
    
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    return render_template('register.html')

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Google Mock Login route (no OAuth required)
@app.route("/auth/google/login")
def google_login():
    """Simple mock Google login without OAuth authentication"""
    try:
        # Create or get demo Google user
        google_user = {
            'username': 'google_user',
            'email': 'user@gmail.com',
            'role': 'Analyst'
        }
        
        # Check if user exists
        user = get_user_by_username(google_user['username'])
        
        if not user:
            # Create demo Google user if doesn't exist
            import secrets
            temp_password = secrets.token_urlsafe(16)
            success, message = register_user(
                username=google_user['username'],
                password=temp_password,
                email=google_user['email'],
                role=google_user['role']
            )
            if not success:
                return render_template('login.html', error=f'Could not create Google user: {message}')
            user = get_user_by_username(google_user['username'])
        
        # Create session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error in google_login: {e}")
        traceback.print_exc()
        return render_template('login.html', error=f'Google login failed: {str(e)}')

# Dashboard page
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    try:
        # Load logs from database
        logs = load_logs()
        
        if logs.empty:
            return f"<h1>Error</h1><p>No logs found in database</p>"
        
        # Mine patterns from messages (check if 'message' column exists)
        message_col = 'message' if 'message' in logs.columns else logs.columns[-1]
        patterns = mine_patterns(logs[message_col])
        
        # Handle prediction on POST
        prediction_results = None
        if request.method == "POST":
            sample_message = request.form.get("message", "")
            if sample_message and model_predict:
                prediction_results = model_predict([sample_message])
        
        # Convert to dictionaries for template
        logs_dict = logs.head(20).to_dict(orient="records") if not logs.empty else []
        patterns_dict = patterns.head(10).to_dict(orient="records") if not patterns.empty else []
        
        return render_template("index.html",
                               logs=logs_dict,
                               patterns=patterns_dict,
                               prediction=prediction_results,
                               user=session.get('username'),
                               role=session.get('role'))
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Error: {error_msg}")
        return f"<h1>Error loading logs</h1><p>{str(e)}</p><pre>{error_msg}</pre>"

@app.route("/api/logs", methods=["GET"])
@login_required
def get_logs_api():
    """API endpoint to fetch logs from database"""
    try:
        logs = load_logs()
        return jsonify(logs.head(50).to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    """API endpoint for prediction without page reload"""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Get prediction (either from trained model or keyword-based fallback)
        result = model_predict([message])
        prediction_label = result[0] if result and len(result) > 0 else "INFO"
        
        return jsonify({
            "success": True,
            "prediction": str(prediction_label),
            "message": message
        })
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=8080)
