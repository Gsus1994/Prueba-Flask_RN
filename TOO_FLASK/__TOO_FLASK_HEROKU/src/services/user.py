from src.utils import security
from src.models.user import UserModel
from passlib.context import CryptContext
from flask import session, request, current_app, jsonify

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def authenticate_user(request):
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password') 

            user = UserModel().get_user_by_username(username)

            if not user or not user.get('hashed_password'):
                return jsonify({"msg": "Invalid credentials"}), 401

            if not UserService.verify_password(password, user['hashed_password']):
                return jsonify({"msg": "Invalid credentials"}), 401

            token = security.create_access_token(user)
            session['username'] = user['username']

            return jsonify({"access_token": token, "token_type": "bearer"})
        except Exception as e:
            current_app.logger.error(f"Error al autenticar usuario {username}: {str(e)}")
            return jsonify({"msg": "Error en el proceso de autenticación"}), 500

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            current_app.logger.error(f"Error al verificar la contraseña: {str(e)}")
            return False
    
    @staticmethod
    def logout_user():
        try:
            username = session.get('username', 'Anonymous')
            session.clear()
            current_app.logger.info(f'Usuario: {username} - Cerrando sesion - IP: {request.remote_addr}')
            return jsonify({"msg": "Sesión cerrada correctamente"}), 200
        except Exception as e:
            current_app.logger.error(f"Error al cerrar sesion para el usuario {username}: {str(e)}")
            return jsonify({"msg": "Error al cerrar la sesion"}), 500