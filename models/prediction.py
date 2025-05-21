import random
import math
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

def predict_returns(investment_amount, risk_tolerance, investment_period):
    """
    Predict investment returns based on amount, risk tolerance, and period.
    Uses RandomForestRegressor for more accurate predictions.
    """
    # Convert inputs to appropriate types
    investment_amount = float(investment_amount)
    risk_tolerance = int(risk_tolerance)
    investment_period = int(investment_period)
    
    # Create a feature dataframe with proper column names
    features = pd.DataFrame({
        'investment_amount': [investment_amount],
        'risk_tolerance': [risk_tolerance],
        'investment_period': [investment_period]
    })
    
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Base return rates based on risk tolerance (1-5)
    base_rates = {
        1: 0.04,  # Very Conservative: ~4%
        2: 0.06,  # Conservative: ~6%
        3: 0.08,  # Moderate: ~8%
        4: 0.10,  # Aggressive: ~10%
        5: 0.12   # Very Aggressive: ~12%
    }
    
    # Get base rate with some randomness
    base_rate = base_rates[risk_tolerance]
    volatility = risk_tolerance * 0.01  # Higher risk = higher volatility
    
    # Train a simple model (this would normally be pre-trained on historical data)
    # For demo purposes, we'll create synthetic training data
    X_train = pd.DataFrame({
        'investment_amount': np.random.uniform(1000, 100000, 100),
        'risk_tolerance': np.random.randint(1, 6, 100),
        'investment_period': np.random.randint(1, 31, 100)
    })
    
    # Generate synthetic returns based on our rules
    y_train = []
    for _, row in X_train.iterrows():
        rt = int(row['risk_tolerance'])
        ip = int(row['investment_period'])
        br = base_rates[rt]
        vol = rt * 0.01
        rand_factor = random.random() * vol - vol/2
        annual_rate = br + rand_factor
        final_multiplier = math.pow((1 + annual_rate), ip)
        y_train.append(final_multiplier - 1)  # Return as percentage
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predict return rate
    predicted_multiplier = model.predict(features)[0] + 1
    predicted_return_rate = round((math.pow(predicted_multiplier, 1/investment_period) - 1) * 100, 2)
    
    # Calculate final value using compound interest formula
    final_value = investment_amount * math.pow((1 + (predicted_return_rate/100)), investment_period)
    final_value = round(final_value, 2)
    
    # Calculate total growth percentage
    total_growth = round(((final_value - investment_amount) / investment_amount) * 100, 2)
    
    # Generate annual returns for chart
    annual_returns = []
    current_value = investment_amount
    
    for year in range(1, investment_period + 1):
        # Add some randomness to each year's return
        year_volatility = (random.random() * volatility - volatility/2)
        year_return_rate = base_rate + year_volatility
        
        # Calculate this year's value
        current_value = current_value * (1 + year_return_rate)
        annual_returns.append({
            'year': year,
            'value': round(current_value, 2)
        })
    
    return {
        'initial_investment': investment_amount,
        'predicted_return_rate': predicted_return_rate,
        'final_value': final_value,
        'total_growth': total_growth,
        'annual_returns': annual_returns
    }

def get_investment_recommendations(risk_tolerance):
    """
    Generate investment recommendations based on risk tolerance.
    This is a simplified model for demonstration purposes.
    """
    risk_tolerance = int(risk_tolerance)
    
    # Asset allocation based on risk tolerance
    allocations = {
        1: {  # Very Conservative
            'Bonds': 70,
            'Stocks': 20,
            'Cash': 10
        },
        2: {  # Conservative
            'Bonds': 60,
            'Stocks': 30,
            'Cash': 10
        },
        3: {  # Moderate
            'Bonds': 40,
            'Stocks': 50,
            'Cash': 10
        },
        4: {  # Aggressive
            'Bonds': 20,
            'Stocks': 70,
            'Alternative Investments': 10
        },
        5: {  # Very Aggressive
            'Bonds': 10,
            'Stocks': 75,
            'Alternative Investments': 15
        }
    }
    
    # Specific investment recommendations
    investments = {
        1: [  # Very Conservative
            {'name': 'Treasury Bonds', 'percentage': 40, 'expected_return': 3.5},
            {'name': 'Municipal Bonds', 'percentage': 30, 'expected_return': 4.0},
            {'name': 'Blue Chip Stocks', 'percentage': 20, 'expected_return': 6.0},
            {'name': 'High-Yield Savings', 'percentage': 10, 'expected_return': 2.0}
        ],
        2: [  # Conservative
            {'name': 'Treasury Bonds', 'percentage': 35, 'expected_return': 3.5},
            {'name': 'Corporate Bonds', 'percentage': 25, 'expected_return': 4.5},
            {'name': 'Dividend Stocks', 'percentage': 30, 'expected_return': 7.0},
            {'name': 'Money Market', 'percentage': 10, 'expected_return': 2.5}
        ],
        3: [  # Moderate
            {'name': 'Corporate Bonds', 'percentage': 30, 'expected_return': 4.5},
            {'name': 'Municipal Bonds', 'percentage': 10, 'expected_return': 4.0},
            {'name': 'Index Funds', 'percentage': 30, 'expected_return': 8.0},
            {'name': 'Growth Stocks', 'percentage': 20, 'expected_return': 10.0},
            {'name': 'Money Market', 'percentage': 10, 'expected_return': 2.5}
        ],
        4: [  # Aggressive
            {'name': 'Corporate Bonds', 'percentage': 20, 'expected_return': 4.5},
            {'name': 'Growth Stocks', 'percentage': 40, 'expected_return': 10.0},
            {'name': 'Small Cap Funds', 'percentage': 20, 'expected_return': 12.0},
            {'name': 'International Stocks', 'percentage': 10, 'expected_return': 9.0},
            {'name': 'REITs', 'percentage': 10, 'expected_return': 8.5}
        ],
        5: [  # Very Aggressive
            {'name': 'High-Yield Bonds', 'percentage': 10, 'expected_return': 6.0},
            {'name': 'Growth Stocks', 'percentage': 35, 'expected_return': 10.0},
            {'name': 'Small Cap Funds', 'percentage': 25, 'expected_return': 12.0},
            {'name': 'Emerging Markets', 'percentage': 15, 'expected_return': 14.0},
            {'name': 'Cryptocurrency', 'percentage': 10, 'expected_return': 20.0},
            {'name': 'Venture Capital', 'percentage': 5, 'expected_return': 25.0}
        ]
    }
    
    return {
        'asset_allocation': allocations[risk_tolerance],
        'specific_investments': investments[risk_tolerance]
    }