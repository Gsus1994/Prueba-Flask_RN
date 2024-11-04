# src/utils/security.py

import jwt
from bson import ObjectId
from functools import wraps
from datetime import datetime, timezone, timedelta
from flask import session, redirect, url_for, request, jsonify, make_response, current_app

def create_access_token(data):
    to_encode = data.copy()
    for key, value in to_encode.items():
        if isinstance(value, ObjectId):
            to_encode[key] = str(value)
    expiration = current_app.config['TOKEN_EXPIRATION']
    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiration)
    })
    secret_key = current_app.config['SECRET_KEY']
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

def verify_token(token):
    try:
        secret_key = current_app.config['SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None