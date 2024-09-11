from flask import Blueprint, request   
from laserfocus import Home

Home = Home()

bp = Blueprint('home', __name__)

# Get states of all entities
@bp.route('/home/get_states', methods=['GET'])
async def get_states():
    response = Home.get_states()
    return response

# Get available services for all entities
@bp.route('/home/get_services', methods=['GET'])
async def get_services():
    response = Home.get_services()
    return response

# Call service actions on your entities
@bp.route('home/call_service', methods=['POST'])
async def home_call_service():
    input_json = request.get_json(force=True)
    response = Home.call_service(input_json['service'])
    return response

# Panels?
@bp.route('/home/get_panels', methods=['GET'])
async def get_panels():
    response = Home.get_panels()
    return response

# Packets
@bp.route('/home/light_off', methods=['POST'])
async def home_light_off():

    input_json = request.get_json(force=True)
    response = Home.light_off(input_json['lightId'])
    return response

@bp.route('/home/light_on', methods=['POST'])
async def home_light_on():

    input_json = request.get_json(force=True)
    response = Home.light_on(input_json['lightId'])
    return response