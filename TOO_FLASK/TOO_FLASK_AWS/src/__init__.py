from src.routes import register_blueprints
from src.config import config_by_name, init_app
from flask import Flask, request, session, redirect, url_for

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    init_app(app)
    register_blueprints(app)

    @app.after_request
    def log_request_info(response):
        user = session.get('username', 'Anonymous')  # Obtiene el usuario de la sesión, o 'Anonymous' si no ha iniciado sesión
        ip = request.remote_addr  # Obtiene la dirección IP del cliente
        app.logger.info(f'Usuario: {user} - {request.method} {request.path} - IP: {ip}')
        return response
    
    @app.route('/')
    def index():
        return redirect(url_for('login.login'))
    
    return app