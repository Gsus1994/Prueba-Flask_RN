#Backend/src/models/user.py

from src.config import mongo
from flask import current_app
from bson.objectid import ObjectId
from src.utils.encryption import encrypt_aes, decrypt_aes

class UserModel:
    def __init__(self):
        self.collection = mongo.db['User_2.0']

    def get_user_by_username(self, username):
        try:
            encrypted_username = encrypt_aes(username)
            user = self.collection.find_one({"username": encrypted_username})
            
            if user:

                user['nombre'] = decrypt_aes(user['nombre'])
                user['apellido'] = decrypt_aes(user['apellido'])
                user['dni'] = decrypt_aes(user['dni'])
                user['fecha_nacimiento'] = decrypt_aes(user['fecha_nacimiento'])
                user['profile_image_url'] = decrypt_aes(user['profile_image_url']) if 'profile_image_url' in user else None
                
            return user
        except Exception as e:
            current_app.logger.error(f"Error al obtener usuario por username {username}: {str(e)}")
            raise e
        
    def get_user_by_id(self, user_id):
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['nombre'] = decrypt_aes(user['nombre'])
                user['apellido'] = decrypt_aes(user['apellido'])
                user['dni'] = decrypt_aes(user['dni'])
                user['fecha_nacimiento'] = decrypt_aes(user['fecha_nacimiento'])
                user['username'] = decrypt_aes(user['username'])
                user['profile_image_url'] = decrypt_aes(user['profile_image_url']) if 'profile_image_url' in user else None
            return user
        except Exception as e:
            current_app.logger.error(f"Error al obtener usuario por ID {user_id}: {str(e)}")
            raise e

    def create_user(self, user_data):
        try:
            user_data['username'] = encrypt_aes(user_data['username'])
            user_data['nombre'] = encrypt_aes(user_data['nombre'])
            user_data['apellido'] = encrypt_aes(user_data['apellido'])
            user_data['dni'] = encrypt_aes(user_data['dni'])
            user_data['fecha_nacimiento'] = encrypt_aes(user_data['fecha_nacimiento'])
            if 'profile_image_url' in user_data and user_data['profile_image_url'] is not None:
                user_data['profile_image_url'] = encrypt_aes(user_data['profile_image_url'])

            self.collection.insert_one(user_data)
            return True
        except Exception as e:
            current_app.logger.error(f"Error al crear usuario: {str(e)}")
            raise e
        
    def update_user_image(self, user_id, updated_data):
        try:
            if 'profile_image_url' in updated_data and updated_data['profile_image_url'] is not None:
                updated_data['profile_image_url'] = encrypt_aes(updated_data['profile_image_url'])

            self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
            return True
        except Exception as e:
            current_app.logger.error(f"Error al actualizar usuario {user_id}: {str(e)}")
            raise e

    def update_user_profile_image(self, user_id, profile_image_url):
        try:
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)

            encrypted_profile_image_url = encrypt_aes(profile_image_url)

            self.collection.update_one(
                {'_id': user_id},
                {'$set': {'profile_image_url': encrypted_profile_image_url}}
            )
        except Exception as e:
            current_app.logger.error(f"Error al actualizar la imagen de perfil para el usuario {user_id}: {str(e)}")
            raise e
    
    def update_user_password(self, email, hashed_password):
        try:
            encrypted_email = encrypt_aes(email)
            result = self.collection.update_one(
                {"username": encrypted_email},
                {"$set": {"hashed_password": hashed_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            current_app.logger.error(f"Error al actualizar la contraseña para {email}: {str(e)}")
            raise e        