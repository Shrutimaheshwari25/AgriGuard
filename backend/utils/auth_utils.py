import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY', 'defaultrefreshsecretkey')

def generate_tokens(user_id):
    access_payload = {
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow(),
        'sub': str(user_id)
    }
    refresh_payload = {
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'sub': str(user_id)
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm='HS256')
    return access_token, refresh_token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] if " " in request.headers['Authorization'] else request.headers['Authorization']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

def verify_refresh_token(token):
    try:
        data = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=['HS256'])
        return data['sub']
    except Exception:
        return None
