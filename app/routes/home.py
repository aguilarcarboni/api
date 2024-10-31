from flask import Blueprint, request   
from app.modules.home import get_services, get_states, call_service, light_off, light_on

bp = Blueprint('home', __name__)

# Get states of all entities
@bp.route('/get_states', methods=['POST'])
async def get_states_route():
    input_json = request.get_json(force=True)
    response = get_states(input_json)
    return response

# Get available services for all entities
@bp.route('/get_services', methods=['POST'])
async def get_services_route():
    input_json = request.get_json(force=True)
    response = get_services(input_json)
    return response

# Call service actions on your entities
@bp.route('/call_service', methods=['POST'])
async def call_service_route():
    input_json = request.get_json(force=True)
    response = call_service(input_json)
    return response

# Packets
@bp.route('/light_off', methods=['POST'])
async def light_off_route():

    input_json = request.get_json(force=True)
    response = light_off(input_json['lightId'])
    return response

@bp.route('/light_on', methods=['POST'])
async def light_on_route():

    input_json = request.get_json(force=True)
    response = light_on(input_json['lightId'])
    return response
