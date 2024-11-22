from flask import Blueprint, request
from src.components.tools import calculate_energy_consumption

bp = Blueprint('tools', __name__)

@bp.route('/power_consumption', methods=['POST'])
async def power_consumption_route():
    payload = request.get_json(force=True)
    response = calculate_energy_consumption(payload['watt_hours'])
    return response
