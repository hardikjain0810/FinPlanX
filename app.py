from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from models.user import User
from models.investment_plan import InvestmentPlan
from models.prediction import predict_returns, get_investment_recommendations
import jwt
import datetime
import os
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure random key in production
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1)

# Create a test user at startup
def create_test_user():
    test_user = User(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        password="password123"
    )
    test_user.save()
    print("Test user created with email: test@example.com and password: password123")

# Call the function to create the test user
create_test_user()

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.find_by_email(data['email'])
            if not current_user:
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Token decode error: {e}")
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Login attempt: {email}")
        
        user = User.find_by_email(email)
        print(f"User found: {user is not None}")
        
        if user:
            password_check = user.check_password(password)
            print(f"Password check result: {password_check}")
            
            if password_check:
                token = jwt.encode({
                    'email': user.email,
                    'exp': datetime.datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
                }, app.config['SECRET_KEY'], algorithm="HS256")
                
                session['token'] = token
                print(f"Login successful, redirecting to dashboard")
                return redirect(url_for('dashboard'))
        
        print(f"Login failed for {email}")
        return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        # Validate if user already exists
        if User.find_by_email(data.get('email')):
            return render_template('register.html', error="Email already registered")
        
        # Validate password match
        if data.get('password') != data.get('confirm_password'):
            return render_template('register.html', error="Passwords do not match")
        
        # Create new user
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            password=data.get('password')
        )
        new_user.save()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    return render_template('dashboard.html', user=current_user)

@app.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    data = request.json
    investment_amount = data.get('investment_amount')
    risk_tolerance = data.get('risk_tolerance')
    investment_period = data.get('investment_period')
    
    # Get predictions and recommendations
    predicted_returns = predict_returns(investment_amount, risk_tolerance, investment_period)
    recommendations = get_investment_recommendations(risk_tolerance)
    
    return jsonify({
        'predicted_returns': predicted_returns,
        'recommendations': recommendations
    })

@app.route('/save-plan', methods=['POST'])
@token_required
def save_plan(current_user):
    data = request.json
    
    plan = InvestmentPlan(
        user_email=current_user.email,
        investment_amount=data.get('investment_amount'),
        risk_tolerance=data.get('risk_tolerance'),
        investment_period=data.get('investment_period'),
        predicted_returns=data.get('predicted_returns'),
        recommendations=data.get('recommendations')
    )
    plan_id = plan.save()
    
    return jsonify({'message': 'Plan saved successfully', 'plan_id': plan_id})

@app.route('/get-plans')
@token_required
def get_plans(current_user):
    plans = InvestmentPlan.find_by_user(current_user.email)
    return jsonify({'plans': plans})

@app.route('/delete-plan/<plan_id>', methods=['DELETE'])
@token_required
def delete_plan(current_user, plan_id):
    plan = InvestmentPlan.find_by_id(plan_id)
    
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    
    if plan.user_email != current_user.email:
        return jsonify({'error': 'Unauthorized'}), 403
    
    plan.delete()
    return jsonify({'message': 'Plan deleted successfully'})

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)