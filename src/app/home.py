from flask import Blueprint, request   
from src.components.home import SmartHome

Home = SmartHome()

bp = Blueprint('home', __name__)

# Get states of all entities
@bp.route('/get_states', methods=['POST'])
async def get_states_route():
    payload = request.get_json(force=True)
    response = Home.get_states(payload)
    return response

# Get available services for all entities
@bp.route('/get_services', methods=['POST'])
async def get_services_route():
    payload = request.get_json(force=True)
    response = Home.get_services(payload)
    return response

# Call service actions on your entities
@bp.route('/call_service', methods=['POST'])
async def call_service_route():
    payload = request.get_json(force=True)
    response = Home.call_service(payload)
    return response

# Packets
@bp.route('/light_off', methods=['POST'])
async def light_off_route():
    payload = request.get_json(force=True)
    response = Home.light_off(payload['lightId'])
    return response

@bp.route('/light_on', methods=['POST'])
async def light_on_route():
    payload = request.get_json(force=True)
    response = Home.light_on(payload['lightId'])
    return response