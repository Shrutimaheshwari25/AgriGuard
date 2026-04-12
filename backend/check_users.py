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

count = users.count_documents({})
print(f"\n📊 Total users in database: {count}\n")

for user in users.find({}, {'username': 1, 'email': 1, '_id': 1}):
    email = user.get('email', 'N/A')
    print(f"   ✅ {user['username']:10} | {email:25} | ID: {user['_id']}")

print("\n🔐 Testing password verification for 'test' user:")
test_user = users.find_one({'username': 'test'})
if test_user:
    is_valid = bcrypt.checkpw('test123'.encode('utf-8'), test_user['password'].encode('utf-8'))
    print(f"   Password 'test123' valid: {'✅ YES' if is_valid else '❌ NO'}")
else:
    print("   ❌ Test user not found!")
