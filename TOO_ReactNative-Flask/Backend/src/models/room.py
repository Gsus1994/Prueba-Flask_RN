from bson import ObjectId
from src.config import mongo
from flask import current_app
from src.utils.encryption import encrypt_aes, decrypt_aes

class RoomModel:
    def __init__(self):
        self.collection = mongo.db['Room']

    def get_rooms_by_dni(self, dni):
        try:
            encrypted_dni = encrypt_aes(dni)
            current_app.logger.info(f"Busqueda realizada para DNI: {dni}")

            rooms = list(self.collection.find({"$or": [{"dniUser1": encrypted_dni}, {"dniUser2": encrypted_dni}]}))
            
            for room in rooms:
                room['dniUser1'] = decrypt_aes(room.get('dniUser1')) if room.get('dniUser1') else None
                room['dniUser2'] = decrypt_aes(room.get('dniUser2')) if room.get('dniUser2') else None
                room['nombreUser1'] = decrypt_aes(room.get('nombreUser1')) if room.get('nombreUser1') else None
                room['nombreUser2'] = decrypt_aes(room.get('nombreUser2')) if room.get('nombreUser2') else None
                room['apellidosUser1'] = decrypt_aes(room.get('apellidosUser1')) if room.get('apellidosUser1') else None
                room['apellidosUser2'] = decrypt_aes(room.get('apellidosUser2')) if room.get('apellidosUser2') else None
                room['fechaCreacionSala'] = decrypt_aes(room.get('fechaCreacionSala')) if room.get('fechaCreacionSala') else None

            
                rooms.sort(key=lambda room: room['fechaCreacionSala'] or '')

            return rooms
        except Exception as e:
            current_app.logger.error(f"Error al obtener rooms por DNI {dni}: {str(e)}")
            raise e

    def get_room_by_id(self, room_id):            
        try:
            room = self.collection.find_one({"_id": ObjectId(room_id)})
            
            if room and 'fechaCreacionSala' in room:
                fecha_creacion = decrypt_aes(room.get('fechaCreacionSala'))
                current_app.logger.info(f"Busqueda realizada para el acuerdo anterior la fecha: {fecha_creacion}")
            else:
                current_app.logger.info("No se encontró la sala o no tiene una fecha de creación definida.")
            
            if room:

                decrypted_room = {
                    "nombreUser1": decrypt_aes(room.get('nombreUser1')) if room.get('nombreUser1') else None,
                    "apellidosUser1": decrypt_aes(room.get('apellidosUser1')) if room.get('apellidosUser1') else None,
                    "dniUser1": decrypt_aes(room.get('dniUser1')) if room.get('dniUser1') else None,
                    "CoordenadasUser1": [(coord['latitude'], coord['longitude']) for coord in room.get('user1Coordinates', [])],
                    "nombreUser2": decrypt_aes(room.get('nombreUser2')) if room.get('nombreUser2') else None,
                    "apellidosUser2": decrypt_aes(room.get('apellidosUser2')) if room.get('apellidosUser2') else None,
                    "dniUser2": decrypt_aes(room.get('dniUser2')) if room.get('dniUser2') else None,
                    "CoordenadasUser2": [(coord['latitude'], coord['longitude']) for coord in room.get('user2Coordinates', [])]
                }

                return decrypted_room
            else:
                return None
        except Exception as e:
            current_app.logger.error(f"Error al obtener room por ID {room_id}: {str(e)}")
            raise e