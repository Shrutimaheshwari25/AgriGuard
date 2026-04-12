import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv()

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/agri_db')
client = MongoClient(mongo_uri)
db = client.get_default_database()
users = db.users

test_user = users.find_one({'username': 'test'})
if test_user:
    print(f"Username: {test_user['username']}")
    print(f"Email: {test_user.get('email', 'N/A')}")
    print(f"Password hash type: {type(test_user['password'])}")
    print(f"Password hash (first 50 chars): {str(test_user['password'])[:50]}")
    
    # Test password checking
    password = 'test123'
    print(f"\n🔐 Testing with password: '{password}'")
    
    stored_hash = test_user['password']
    if isinstance(stored_hash, bytes):
        hash_bytes = stored_hash
    else:
        hash_bytes = stored_hash.encode('utf-8')
    
    print(f"Hash bytes (first 30): {hash_bytes[:30]}")
    
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), hash_bytes)
        print(f"Password match: {'✅ YES' if result else '❌ NO'}")
    except Exception as e:
        print(f"❌ Error checking password: {e}")
