#Backend/src/services/user.py

import uuid
from datetime import datetime
from src.utils import security
from src.services.S3 import S3Service
from src.models.user import UserModel
from passlib.context import CryptContext
from werkzeug.utils import secure_filename
from flask import session, request, current_app, jsonify, g

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def register_user(request):

        try:
            data = request.form

            fecha_nacimiento = data.get('fecha_nacimiento')
            nombre = data.get('nombre')
            apellido = data.get('apellidos')
            dni = data.get('dni')
            username = data.get('email')
            password = data.get('password')
            profile_image = request.files.get('profile_image')

            if not username or not password or not nombre or not apellido or not dni or not fecha_nacimiento:
                return jsonify({"msg": "Todos los campos son obligatorios"}), 400

            existing_user = UserModel().get_user_by_username(username)
            if existing_user:
                return jsonify({"msg": "El email del usuario ya ha sido registrado."}), 400

            hashed_password = pwd_context.hash(password)

            profile_image_url = None
            if profile_image:
                if not profile_image.mimetype.startswith('image/'):
                    return jsonify({"msg": "Solo se permiten archivos con formato de imagen"}), 400

                unique_filename = f"{uuid.uuid4()}-{secure_filename(profile_image.filename)}"
                profile_image_url = S3Service().upload_file(profile_image, unique_filename)

            user_data = {
                "username": username,
                "hashed_password": hashed_password,
                "nombre": nombre,
                "apellido": apellido,
                "dni": dni,
                "fecha_nacimiento": fecha_nacimiento,
                "profile_image_url": profile_image_url,
                "created_at": str(datetime.utcnow())
            }

            UserModel().create_user(user_data)

            current_app.logger.info(f"Usuario {username} creado exitosamente.")
            return jsonify({"msg": "Usuario creado exitosamente"}), 201

        except Exception as e:
            current_app.logger.error(f"Error al registrar usuario {username}: {str(e)}")
            return jsonify({"msg": "Error en el proceso de registro"}), 500

    @staticmethod
    def authenticate_user(request):
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"msg": "Faltan credenciales"}), 400

            user = UserModel().get_user_by_username(username)

            if not user or not user.get('hashed_password'):
                return jsonify({"msg": "Credenciales inválidas"}), 401

            if not UserService.verify_password(password, user['hashed_password']):
                return jsonify({"msg": "Credenciales inválidas"}), 401

            token_data = {
                "_id": str(user['_id']),
                "username": user['username']
            }

            token = security.create_access_token(token_data)

            session['username'] = user['username']

            return jsonify({
                "access_token": token,
                "token_type": "bearer",
            })
        except Exception as e:
            current_app.logger.error(f"Error al autenticar usuario {username}: {str(e)}")
            return jsonify({"msg": "Error en el proceso de autenticación"}), 500

    @staticmethod
    def get_user_profile():
        try:
            user = g.user

            if user:
                user_db = UserModel().get_user_by_id(user['_id'])
                if user_db:
                    profile_image_url = None
                    if user_db.get('profile_image_url'):
                        filename = user_db['profile_image_url'].split('/')[-1]
                        profile_image_url = S3Service().generate_presigned_url(filename)

                    user_data = {
                        "nombre": user_db['nombre'],
                        "apellido": user_db['apellido'],
                        "dni": user_db['dni'],
                        "fecha_nacimiento": user_db['fecha_nacimiento'],
                        "email": user_db['username'],
                        "profile_image_url": profile_image_url
                    }
                    return jsonify(user_data), 200
                else:
                    return jsonify({"msg": "No se encontró el usuario"}), 404
            else:
                return jsonify({"msg": "Usuario no autenticado"}), 401
        except Exception as e:
            current_app.logger.error(f"Error al obtener el perfil del usuario: {str(e)}")
            return jsonify({"msg": "Error al obtener el perfil"}), 500

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            current_app.logger.error(f"Error al verificar la contraseña: {str(e)}")
            return False

    @staticmethod
    def update_profile_image(request):
        try:
            user = g.user
            if not user:
                return jsonify({"msg": "Usuario no autenticado"}), 401

            profile_image = request.files.get('profile_image')

            if not profile_image:
                return jsonify({"msg": "No se envió ninguna imagen"}), 400

            if not profile_image.mimetype.startswith('image/'):
                return jsonify({"msg": "Solo se permiten archivos con formato de imagen"}), 400
            
            user_db = UserModel().get_user_by_id(user['_id'])

            if user_db.get('profile_image_url'):
                previous_filename = user_db['profile_image_url'].split('/')[-1]
                S3Service().delete_file(previous_filename)

            unique_filename = f"{uuid.uuid4()}-{secure_filename(profile_image.filename)}"
            profile_image_url = S3Service().upload_file(profile_image, unique_filename)

            UserModel().update_user_profile_image(user['_id'], profile_image_url)

            return jsonify({"msg": "Imagen de perfil actualizada correctamente", "profile_image_url": profile_image_url}), 200

        except Exception as e:
            current_app.logger.error(f"Error al actualizar la imagen de perfil del usuario {user['username']}: {str(e)}")
            return jsonify({"msg": "Error al actualizar la imagen de perfil"}), 500

    @staticmethod
    def logout_user():
        try:
            username = session.get('username', 'Anonymous')
            session.clear()
            current_app.logger.info(f'Usuario: {username} - Cerrando sesión - IP: {request.remote_addr}')
            return jsonify({"msg": "Sesión cerrada correctamente"}), 200
        except Exception as e:
            current_app.logger.error(f"Error al cerrar sesión para el usuario {username}: {str(e)}")
            return jsonify({"msg": "Error al cerrar la sesión"}), 500
        
    @staticmethod
    def get_user_by_email(email):
        user = UserModel().get_user_by_username(email)
        return user

    @staticmethod
    def update_user_password(email, new_password):
        try:
            hashed_password = pwd_context.hash(new_password)
            result = UserModel().update_user_password(email, hashed_password)
            if result:
                current_app.logger.info(f"Contraseña actualizada para {email}")
                return True
            else:
                current_app.logger.error(f"No se pudo actualizar la contraseña para {email}")
                return False
        except Exception as e:
            current_app.logger.error(f"Error al actualizar la contraseña para {email}: {str(e)}")
            return False