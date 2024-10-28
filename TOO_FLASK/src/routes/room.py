from src.services.room import RoomService
from src.utils.security import token_required, login_required, nocache
from flask import Blueprint, render_template, jsonify, current_app

rooms_bp = Blueprint('rooms', __name__)

@rooms_bp.route('/show_map')
@login_required
@nocache
def show_map():
    try:
        return render_template('views/map.html')
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /show_map: {str(e)}")
        return jsonify({"msg": "Error al cargar el mapa"}), 500

@rooms_bp.route('/rooms/obtener_acuerdos', methods=['POST'])
@token_required
def obtener_acuerdos():
    try:
        return RoomService.acuerdos()
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /rooms/obtener_acuerdos: {str(e)}")
        return jsonify({"msg": "Error al obtener acuerdos"}), 500

@rooms_bp.route('/rooms/itinerario', methods=['POST'])
@token_required
def itinerario():
    try:
        return RoomService.obterner_itinerario()
    except Exception as e:
        current_app.logger.error(f"Error en la ruta /rooms/itinerario: {str(e)}")
        return jsonify({"msg": "Error al obtener el itinerario"}), 500