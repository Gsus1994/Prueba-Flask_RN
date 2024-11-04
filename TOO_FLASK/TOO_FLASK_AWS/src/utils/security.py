import jwt
from bson import ObjectId
from functools import wraps
from flask import make_response
from src.config import config_by_name
from datetime import datetime, timezone, timedelta
from flask import session, redirect, url_for, request, jsonify

def create_access_token(data):

    to_encode = data.copy()
    for key, value in to_encode.items():
        if isinstance(value, ObjectId):
            to_encode[key] = str(value)
    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=config_by_name['development'].TOKEN_EXPIRATION)
    })

    return jwt.encode(to_encode, config_by_name['development'].SECRET_KEY, algorithm="HS256")


def verify_token(token):
    try:
        # Decodifica el token usando la clave secreta
        payload = jwt.decode(token, config_by_name['development'].SECRET_KEY, algorithms=["HS256"])
        return payload  # Devuelve el payload si el token es válido
    except jwt.ExpiredSignatureError:
        return None  # El token ha expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Intenta obtener el token de la cabecera 'Authorization'
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Elimina el 'Bearer '

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401  # Si no hay token, devuelve un error

        try:
            # Verifica el token
            data = verify_token(token)
            if data is None:
                return jsonify({'message': 'Token is invalid or expired!'}), 401
            session['user'] = data  # Opcional: puedes almacenar los datos del usuario en la sesión
        except Exception as e:
            return jsonify({'message': 'Something went wrong', 'error': str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function

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