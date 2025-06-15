from ib_insync import Contract, Order
from src.utils.connectors.tws import TWSConnector
from src.utils.exception import handle_exception
from src.utils.logger import logger

logger.announcement("Initializing Orders Service", 'info')
logger.announcement("Orders Service initialized", 'success')

tws = TWSConnector()

@handle_exception
def place_order(contract: Contract, order: Order):
    logger.info(f"Placing order: {order}")
    return tws.place_order(contract, order)

@handle_exception
def order_status(orderId: int):
    logger.info(f"Fetching account order status information")
    return tws.order_status(orderId)

@handle_exception
def cancel_order(orderId: int):
    logger.info(f"Cancelling order: {orderId}")
    return tws.cancel_order(orderId)

@handle_exception
def exec_details(orderId: int, contract: Contract):
    logger.info(f"Fetching account exec details information")
    return tws.exec_details(orderId, contract)

@handle_exception
def completed_orders():
    logger.info(f"Fetching account completed orders information")
    return tws.completed_orders()

@handle_exception
def open_orders():
    logger.info(f"Fetching account open orders information")
    return tws.open_orders()

@handle_exception
def close_all_positions():
    logger.info(f"Closing all positions")
    return tws.close_all_positions()