import re
from src.models.room import RoomModel
from flask import request, jsonify, current_app

class RoomService:
    
    @staticmethod
    def Obtener_acuerdos():
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