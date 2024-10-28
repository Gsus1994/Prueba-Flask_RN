#Backend/src/routes/user.py

from src.utils import security
from src.services.user import UserService
from flask import Blueprint, jsonify, request, current_app
from src.services.password_reset import PasswordResetService


auth_bp = Blueprint('login', __name__)


@auth_bp.route('/register', methods=['POST'])
def signup():
    try:
        response = UserService.register_user(request)
        return response
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /register: {str(e)}")
        return jsonify({"msg": "Error en el proceso de registro"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        response = UserService.authenticate_user(request)
        return response
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /login: {str(e)}")
        return jsonify({"msg": "Error en el proceso de login"}), 500

@auth_bp.route('/profile', methods=['GET'])
@security.token_required
def get_profile():
    try:
        response = UserService.get_user_profile()
        return response
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /profile: {str(e)}")
        return jsonify({"msg": "Error al obtener el perfil"}), 500
    
@auth_bp.route('/profile/image', methods=['PUT'])
@security.token_required
def update_profile_image():
    return UserService.update_profile_image(request)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        response = UserService.logout_user()
        return response
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /logout: {str(e)}")
        return jsonify({"msg": "Error al cerrar la sesión"}), 500
    

@auth_bp.route('/password-reset/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"msg": "El email es requerido"}), 400

    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({"msg": "No se encontró el email introducido"}), 404

    reset_service = PasswordResetService()
    code = reset_service.generate_code()
    reset_service.store_code(email, code)

    print(email,code)

    if reset_service.send_reset_email(email, code):
        return jsonify({"msg": "Se ha enviado un correo con el código de restablecimiento"}), 200
    else:
        return jsonify({"msg": "Error al enviar el correo de restablecimiento"}), 500



@auth_bp.route('/password-reset/confirm', methods=['POST'])
def confirm_password_reset():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')

    if not email or not code or not new_password:
        return jsonify({"msg": "Todos los campos son requeridos"}), 400

    reset_service = PasswordResetService()
    if not reset_service.verify_code(email, code):
        return jsonify({"msg": "Código inválido o expirado"}), 400

    if not UserService.update_user_password(email, new_password):
        return jsonify({"msg": "Error al actualizar la contraseña"}), 500

    return jsonify({"msg": "Contraseña actualizada exitosamente"}), 200