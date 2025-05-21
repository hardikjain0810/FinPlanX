from pymongo import MongoClient
from bson import ObjectId
import datetime

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['investment_advisor']
plans_collection = db['investment_plans']

class InvestmentPlan:
    def __init__(self, user_email, investment_amount, risk_tolerance, investment_period, predicted_returns, recommendations, id=None):
        self.id = id
        self.user_email = user_email
        self.investment_amount = investment_amount
        self.risk_tolerance = risk_tolerance
        self.investment_period = investment_period
        self.predicted_returns = predicted_returns
        self.recommendations = recommendations
        self.created_at = datetime.datetime.utcnow()
    
    def save(self):
        plan_data = {
            'user_email': self.user_email,
            'investment_amount': self.investment_amount,
            'risk_tolerance': self.risk_tolerance,
            'investment_period': self.investment_period,
            'predicted_returns': self.predicted_returns,
            'recommendations': self.recommendations,
            'created_at': self.created_at
        }
        
        result = plans_collection.insert_one(plan_data)
        self.id = str(result.inserted_id)
        print(f"Plan saved to MongoDB with ID: {self.id}")
        return self.id
    
    def delete(self):
        if self.id:
            plans_collection.delete_one({'_id': ObjectId(self.id)})
            print(f"Plan deleted from MongoDB: {self.id}")
            return True
        return False
    
    @staticmethod
    def find_by_id(plan_id):
        try:
            plan_data = plans_collection.find_one({'_id': ObjectId(plan_id)})
            if plan_data:
                plan = InvestmentPlan(
                    user_email=plan_data['user_email'],
                    investment_amount=plan_data['investment_amount'],
                    risk_tolerance=plan_data['risk_tolerance'],
                    investment_period=plan_data['investment_period'],
                    predicted_returns=plan_data['predicted_returns'],
                    recommendations=plan_data['recommendations'],
                    id=str(plan_data['_id'])
                )
                return plan
        except Exception as e:
            print(f"Error finding plan by ID: {e}")
        return None
    
    @staticmethod
    def find_by_user(user_email):
        plans_data = plans_collection.find({'user_email': user_email}).sort('created_at', -1)
        plans = []
        
        for plan_data in plans_data:
            plan = {
                'id': str(plan_data['_id']),
                'user_email': plan_data['user_email'],
                'investment_amount': plan_data['investment_amount'],
                'risk_tolerance': plan_data['risk_tolerance'],
                'investment_period': plan_data['investment_period'],
                'predicted_returns': plan_data['predicted_returns'],
                'recommendations': plan_data['recommendations'],
                'created_at': plan_data['created_at']
            }
            plans.append(plan)
        
        return plans