from flask import Blueprint, request   
from src.components.home import SmartHome
Home = SmartHome()

bp = Blueprint('home', __name__)

def create_smart_home_routes():

    # Get states of all entities
    @bp.route('/get_states', methods=['POST'])
    async def get_states_route():
        payload = request.get_json(force=True)
        return Home.get_states(payload)

    # Get available services for all entities
    @bp.route('/get_services', methods=['POST'])
    async def get_services_route():
        payload = request.get_json(force=True)
        return Home.get_services(payload)

    # Call service actions on your entities
    @bp.route('/call_service', methods=['POST'])
    async def call_service_route():
        payload = request.get_json(force=True)
        return Home.call_service(payload)

    # Packets
    @bp.route('/light_off', methods=['POST'])
    async def light_off_route():
        payload = request.get_json(force=True)
        return Home.light_off(payload['lightId'])

    @bp.route('/light_on', methods=['POST'])
    async def light_on_route():
        payload = request.get_json(force=True)
        return Home.light_on(payload['lightId'])

def create_closet_routes():
    @bp.route('/closet/create', methods=['POST'])
    async def closet_create_route():
        payload = request.get_json(force=True)
        return Home.read_closet()

create_closet_routes()
create_smart_home_routes()