from flask import Blueprint
from src.components.orders import open_orders, completed_orders, place_order
from src.components.orders import order_status
from src.components.orders import cancel_order
from src.components.orders import exec_details
from src.components.orders import close_all_positions
bp = Blueprint('orders', __name__)

@bp.route('/place-order', methods=['POST'])
def place_order_route():
    return place_order()

@bp.route('/order-status', methods=['GET'])
def order_status_route():
    return order_status()

@bp.route('/cancel-order', methods=['POST'])
def cancel_order_route():
    return cancel_order()

@bp.route('/open-orders', methods=['GET'])
def open_orders_route():
    return open_orders()

@bp.route('/completed-orders', methods=['GET'])
def completed_orders_route():
    return completed_orders()

@bp.route('/exec-details', methods=['GET'])
def exec_details_route():
    return exec_details()

@bp.route('/close-all-positions', methods=['POST'])
def close_all_positions_route():
    return close_all_positions()