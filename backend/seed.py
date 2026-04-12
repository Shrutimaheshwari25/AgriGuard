"""
Seed script to create test users in MongoDB
Run this once to populate the database with test accounts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv()

def get_db():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/agri_db')
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    return db

def seed_test_users():
    db = get_db()
    users = db.users
    
    # Drop existing test data (optional)
    # users.delete_many({'username': {'$in': ['test', 'demo', 'admin']}})
    
    test_users = [
        {
            'username': 'test',
            'email': 'test@agriguard.com',
            'password': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        },
        {
            'username': 'demo',
            'email': 'demo@agriguard.com',
            'password': bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        },
        {
            'username': 'admin',
            'email': 'admin@agriguard.com',
            'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
    ]
    
    for user in test_users:
        existing = users.find_one({'$or': [{'username': user['username']}, {'email': user['email']}]})
        if existing:
            print(f"⏭️  User '{user['username']}' already exists, skipping...")
        else:
            result = users.insert_one(user)
            print(f"✅ Created user '{user['username']}' (ID: {result.inserted_id})")
    
    print("\n📋 Test Credentials:")
    print("   Username: test       | Password: test123")
    print("   Username: demo       | Password: demo123")
    print("   Username: admin      | Password: admin123")

if __name__ == '__main__':
    try:
        print("🌱 Seeding test users...\n")
        seed_test_users()
        print("\n✨ Seeding complete!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
