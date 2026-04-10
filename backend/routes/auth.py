from flask import Blueprint, request, jsonify
from utils.db import get_db
from utils.auth_utils import generate_tokens, token_required, verify_refresh_token
from utils.limiter import limiter
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'Missing username, email, or password'}), 400

    db = get_db()
    users = db.users

    if users.find_one({'$or': [{'username': username}, {'email': email}]}):
        return jsonify({'message': 'Username or Email already exists'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user_id = users.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password.decode('utf-8')
    }).inserted_id

    return jsonify({'message': 'User created successfully', 'user_id': str(user_id)}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing credentials'}), 400

    db = get_db()
    user = db.users.find_one({'$or': [{'username': username}, {'email': username}]})

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token, refresh_token = generate_tokens(str(user['_id']))
    return jsonify({'token': access_token, 'refresh_token': refresh_token, 'username': user['username']}), 200

@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit("10 per minute")
def refresh():
    data = request.get_json(silent=True) or {}
    refresh_token_str = data.get('refresh_token')
    if not refresh_token_str:
        return jsonify({'message': 'Refresh token missing'}), 400
    user_id = verify_refresh_token(refresh_token_str)
    if not user_id:
        return jsonify({'message': 'Invalid or expired refresh token'}), 401
    
    access_token, new_refresh_token = generate_tokens(user_id)
    return jsonify({'token': access_token, 'refresh_token': new_refresh_token}), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user_id):
    db = get_db()
    from bson.objectid import ObjectId
    user = db.users.find_one({'_id': ObjectId(current_user_id)}, {'password': 0})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user['_id'] = str(user['_id'])
    return jsonify({'user': user}), 200
