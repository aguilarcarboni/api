from flask import Blueprint, request   
from laserfocus import Home

Home = Home()

bp = Blueprint('home', __name__)

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