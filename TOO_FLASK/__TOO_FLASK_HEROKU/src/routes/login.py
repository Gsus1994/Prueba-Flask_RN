from src.services.user import UserService
from flask import Blueprint, render_template, jsonify, request, current_app

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            response = UserService.authenticate_user(request)
            return response
        return render_template('auth/login.html')
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /login: {str(e)}")
        return jsonify({"msg": "Error en el proceso de login"}), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    try:
        response = UserService.logout_user()
        return response
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /logout: {str(e)}")
        return jsonify({"msg": "Error al cerrar la sesión"}), 500