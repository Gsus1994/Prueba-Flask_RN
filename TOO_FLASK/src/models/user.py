from src.config import mongo
from flask import current_app

class UserModel:
    def __init__(self):
        self.collection = mongo.db['Polis']

    def get_user_by_username(self, username):
        try:
            return self.collection.find_one({"username": username})
        except Exception as e:
            current_app.logger.error(f"Error al obtener usuario por username {username}: {str(e)}")
            raise e