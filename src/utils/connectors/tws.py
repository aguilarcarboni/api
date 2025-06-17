from ib_insync import *
from src.utils.logger import logger
import time
import math
import os
from datetime import datetime

logger.announcement("Initializing TWS Connector", 'info')
logger.announcement("TWS Connector initialized", 'success')

class TWSConnector:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TWSConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if TWSConnector._initialized:
            return
        
        self.ib = IB()
        self.host = os.getenv('IBKR_HOST', None)
        self.port = int(os.getenv('IBKR_PORT', None))
        self.connect()
        TWSConnector._initialized = True

    def connect(self) -> bool:
        logger.info(f"Connecting to IBKR at {self.host}:{self.port}")
        try:
            if self.host is None or self.port is None:
                raise Exception("IBKR_HOST and IBKR_PORT must be set in the environment variables.")
            
            self.ib.connect(self.host, self.port, clientId=1)
            if self.ib.isConnected():
                logger.success("Connected to IBKR")
                return True
            else:
                logger.error("Failed to connect to IBKR")
                return False
        except Exception as e:
            logger.error(f"Error connecting to IB: {str(e)}")
            raise Exception(f"Error connecting to IB: {str(e)}")
        
    def disconnect(self) -> bool:
        logger.info("Disconnecting from IBKR")
        if self.ib.isConnected():
            try:
                self.ib.disconnect()
                logger.success("Disconnected from IBKR")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from IB: {str(e)}")
                return False
        return False

    # Market
    def historical_data(self, contract: Contract, period: str = '1 Y') -> list:
        logger.info(f"Getting historical data for {contract} to {period}")
        current_date = datetime.now().strftime('%Y%m%d %H:%M:%S')
        try:
            historical_data_response = self.ib.reqHistoricalData(
                contract, 
                endDateTime=current_date, 
                durationStr=period,  
                barSizeSetting='1 day', 
                whatToShow='TRADES', 
                useRTH=1
            )
            historical_data = []
            for bar in historical_data_response:
                historical_data.append(bar.dict())
            
            logger.success(f"Successfully got historical data")
            return historical_data
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            raise Exception(f"Error getting historical data: {str(e)}")

    def current_data(self, contract: Contract) -> dict:
        logger.info(f"Getting latest price")
        try:
            self.ib.reqMarketDataType(3)
            ticker = self.ib.reqMktData(contract, '233', False, False, [])
            
            # Wait for market data
            timeout = 10  # 10 second timeout
            start_time = time.time()
            while math.isnan(ticker.last) and (time.time() - start_time) < timeout:
                self.ib.sleep(0.1)
                logger.info(f"Waiting for market data...")
            
            if math.isnan(ticker.last):
                raise Exception("Timeout waiting for market data")
            
            logger.success(f"Successfully got latest price: {ticker.last}")
            stock_data = {
                'last': ticker.last,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'bidSize': ticker.bidSize,
                'askSize': ticker.askSize
            }
            return stock_data
        except Exception as e:
            logger.error(f"Error getting latest price: {str(e)}")
            raise Exception(f"Error getting latest price: {str(e)}")
    
    # Account
    def account_summary(self) -> list:
        logger.info("Getting account summary")
        try:
            account_summary = self.ib.accountSummary()
            logger.success(f"Successfully got account summary")
            formatted_summary = []
            for summary in account_summary:
                formatted_summary.append({
                    'account': summary.account,
                    'tag': summary.tag,
                    'value': summary.value,
                    'currency': summary.currency,
                    'modelCode': summary.modelCode
                })
            return formatted_summary
        except Exception as e:
            logger.error(f"Error getting account summary: {str(e)}")
            raise Exception(f"Error getting account summary: {str(e)}")

    def positions(self) -> list:
        logger.info("Getting positions")
        try:
            positions = self.ib.positions()
            logger.info(f"You have {len(positions)} positions overall")
            
            # Convert positions to serializable format
            formatted_positions = []
            for pos in positions:
                formatted_positions.append(pos.dict())
            
            logger.success(f"Successfully got positions")
            return formatted_positions
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            raise Exception(f"Error getting positions: {str(e)}")

    def portfolio(self) -> list:
        logger.info("Getting portfolio")
        try:
            portfolio_response = self.ib.portfolio()
            logger.success(f"Successfully got portfolio")
            formatted_portfolio = []
            for item in portfolio_response:
                formatted_portfolio.append(item.dict())
            return formatted_portfolio
        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            raise Exception(f"Error getting portfolio: {str(e)}")
        
    def pnl(self) -> list:
        logger.info("Getting PNL")
        try:
            pnl_response = self.ib.pnl()
            logger.success(f"Successfully got PNL")
            formatted_pnl = []
            for item in pnl_response:
                formatted_pnl.append(item.dict())
            return formatted_pnl
        except Exception as e:
            logger.error(f"Error getting PNL: {str(e)}")
            raise Exception(f"Error getting PNL: {str(e)}")

    def pnl_single(self, contract: Contract) -> list:
        logger.info(f"Getting PNL for {contract}")
        try:
            pnl_single_response = self.ib.pnlSingle(contract)
            logger.success(f"Successfully got PNL for {contract}")
            formatted_pnl_single = []
            for item in pnl_single_response:
                formatted_pnl_single.append(item.dict())
            return formatted_pnl_single
        except Exception as e:  
            logger.error(f"Error getting PNL for {contract}: {str(e)}")
            raise Exception(f"Error getting PNL for {contract}: {str(e)}")

    # Orders
    def order_status(self, orderId: int) -> dict:
        logger.info(f"Getting order status: {orderId}")
        try:
            order = self.ib.orderStatus(orderId)
            logger.success(f"Successfully got order status")
            return order.dict()
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            raise Exception(f"Error getting order status: {str(e)}")
        
    def completed_orders(self) -> list:
        logger.info("Getting completed orders")
        try:
            orders_response = self.ib.reqCompletedOrders(False)
            formatted_orders = []
            for order in orders_response:
                formatted_orders.append(order.dict())
            logger.info(f"Successfully got {len(formatted_orders)} completed orders")
            logger.success(f"Successfully got {len(formatted_orders)} completed orders")
            return formatted_orders
        except Exception as e:
            logger.error(f"Error getting completed orders: {str(e)}")
            raise Exception(f"Error getting completed orders: {str(e)}")

    def open_orders(self) -> list:
        logger.info("Getting open orders")
        try:
            orders_response = self.ib.openOrders()
            formatted_orders = []
            for order in orders_response:
                formatted_orders.append(order.dict())
            logger.info(f"Successfully got {len(formatted_orders)} open orders")
            logger.success(f"Successfully got {len(formatted_orders)} open orders")
            return formatted_orders
        except Exception as e:
            logger.error(f"Error getting open orders: {str(e)}")
            raise Exception(f"Error getting open orders: {str(e)}")


    def place_order(self, contract: Contract, order: Order) -> dict:
        logger.info(f"Placing order: {order}")
        try:
            self.ib.qualifyContracts(contract)
            trade = self.ib.placeOrder(contract, order)
            logger.success(f"Successfully placed order")
            return trade.dict()
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise Exception(f"Error placing order: {str(e)}")

    def cancel_order(self, orderId: int) -> bool:
        logger.info(f"Cancelling order: {orderId}")
        try:
            self.ib.cancelOrder(orderId)
            logger.success(f"Successfully cancelled order")
            return True
        except Exception as e:  
            logger.error(f"Error cancelling order: {str(e)}")
            raise Exception(f"Error cancelling order: {str(e)}")
    
    def exec_details(self, orderId: int, contract: Contract) -> list:
        logger.info(f"Getting exec details: {orderId}")
        try:
            exec_details = self.ib.execDetails(orderId, contract)
            logger.success(f"Successfully got exec details")
            formatted_exec_details = []
            for item in exec_details:
                formatted_exec_details.append(item.dict())
            return formatted_exec_details
        except Exception as e:
            logger.error(f"Error getting exec details: {str(e)}")
            raise Exception(f"Error getting exec details: {str(e)}")
    
    def close_all_positions(self) -> bool:
        logger.info("Closing all positions")
        try:
            orders = self.ib.orders()
            for order in orders:
                self.ib.cancelOrder(order)
            logger.success("Successfully closed all positions")
            return True
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")
            raise Exception(f"Error closing all positions: {str(e)}")