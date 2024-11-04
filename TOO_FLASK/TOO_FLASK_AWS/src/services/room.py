import re
from src.models.room import RoomModel
from flask import request, jsonify, current_app

class RoomService:
    
    @staticmethod
    def acuerdos():
        dni = request.json.get('dni')    
        
        if not dni:        
            return jsonify({"error": "DNI no proporcionado"}), 400
        
        if not re.match(r"^\d{8}[A-Z]$", dni):        
            return jsonify({"error": "DNI incorrecto. Debe contener 8 números seguidos de una letra mayúscula."}), 400
        
        try:
            agreements = RoomModel().get_rooms_by_dni(dni)        
        except Exception as e:
            current_app.logger.error(f"Error al buscar acuerdos para DNI {dni}: {str(e)}")
            return jsonify({"error": "Error al buscar acuerdos."}), 500
        
        if not agreements:        
            return jsonify({"error": "No se encontraron acuerdos para el DNI proporcionado"}), 404

        for agreement in agreements:
            agreement['_id'] = str(agreement['_id'])
        
        return jsonify(agreements), 200
    
    @staticmethod
    def obterner_itinerario():
        agreement_id = request.json.get('agreement_id')

        if not agreement_id:
            return jsonify({"error": "ID del acuerdo no proporcionado"}), 400

        try:
            room_model = RoomModel()
            agreement_details = room_model.get_room_by_id(agreement_id)
        except Exception as e:
            current_app.logger.error(f"Error al obtener detalles del acuerdo con ID {agreement_id}: {str(e)}")
            return jsonify({"error": "Error al obtener detalles del acuerdo."}), 500

        if not agreement_details:
            return jsonify({"error": "No se encontraron detalles para el ID proporcionado"}), 404

        return jsonify(agreement_details), 200