#Backend/src/__init__py

from flask_cors import CORS
from src.routes import register_blueprints
from src.utils.encryption import decrypt_aes
from src.config import config_by_name, init_app
from flask import Flask, request, session, redirect, url_for

def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_by_name[config_name])
    
    init_app(app)
    register_blueprints(app)

    @app.after_request
    def log_request_info(response):
        user = session.get('username', 'Anonymous')
        ip = request.remote_addr
        app.logger.info(f'Email: {decrypt_aes(user)} -- Metodo: {request.method} -- Ruta: {request.path} -- IP: {ip}')
        return response
    
    @app.route('/')
    def index():
        return redirect(url_for('login.login'))
    
    return app