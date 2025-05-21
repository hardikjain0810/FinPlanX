import bcrypt
from pymongo import MongoClient
import os

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['investment_advisor']
users_collection = db['users']

class User:
    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = self._hash_password(password) if isinstance(password, str) and not password.startswith('$2b$') else password
    
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        except Exception as e:
            print(f"Password check error: {e}")
            return False
    
    def save(self):
        user_data = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'password': self.password
        }
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': self.email})
        if existing_user:
            # Update existing user
            users_collection.update_one({'email': self.email}, {'$set': user_data})
        else:
            # Insert new user
            users_collection.insert_one(user_data)
        
        print(f"User saved to MongoDB: {self.email}")
    
    @staticmethod
    def find_by_email(email):
        user_data = users_collection.find_one({'email': email})
        if user_data:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                password=user_data['password']
            )
            return user
        print(f"User not found in MongoDB: {email}")
        return None