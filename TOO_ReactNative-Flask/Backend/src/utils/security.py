#Backend/src/utils/security.py

import jwt
from functools import wraps
from flask import make_response
from src.config import config_by_name
from datetime import datetime, timezone, timedelta
from flask import session, redirect, url_for, request, jsonify, current_app, g

def create_access_token(data):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=config_by_name['production'].TOKEN_EXPIRATION)
    })

    return jwt.encode(to_encode, config_by_name['production'].SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, config_by_name['production'].SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token es requerido'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = data['_id']
            g.user = {'_id': user_id, 'username': data['username']}
        except Exception as e:
            current_app.logger.error(f"Token inválido: {str(e)}")
            return jsonify({'message': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorated

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function