import json
from websocket import create_connection, WebSocketConnectionClosedException
import os
import time
from functools import wraps

from src.utils.logger import logger
from src.utils.response import Response

def retry_on_websocket_error(max_retries=3, initial_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except WebSocketConnectionClosedException:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to execute {func.__name__} after {max_retries} attempts")
                        raise
                    logger.warning(f"WebSocket connection lost. Attempting to reconnect... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    self.connect()
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class SmartHome:

    def __init__(self):
        logger.announcement('Initializing Smart Home', 'info')
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyZWQwMmIyNjg1MmU0NGRiODUwMTc3ODUwMWUwM2ViMCIsImlhdCI6MTczNTM2MjI5OCwiZXhwIjoyMDUwNzIyMjk4fQ.oo-_llblCQUSCPVnb8aWAc_AFm-F14GJhp-TeGZphZo"
        self.ws = None
        self.nextId = 0
        self.connect()

    def connect(self):
        """Establish websocket connection and authenticate"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            
        try:
            logger.info(f"Connecting to Smart Home at {os.getenv('HOME_ASSISTANT_URL')}/api/websocket")
            self.ws = create_connection(f"{os.getenv('HOME_ASSISTANT_URL')}/api/websocket")
            logger.success("WebSocket connection established")
            
            # Handle initial auth
            response = json.loads(self.ws.recv())
            if response['type'] != "auth_required":
                raise Exception("Unexpected response type during authentication")
            
            # Send auth token
            self.ws.send(json.dumps({'type': 'auth', 'access_token': self.token}))
            response = json.loads(self.ws.recv())
            if response['type'] != "auth_ok":
                raise Exception("Authentication failed")
                
            logger.announcement("Successfully initialized Smart Home.", 'success')
        except Exception as e:
            logger.error(f"Smart Home connection failed: {str(e)}")
            raise

    def disconnect(self):
        """Safely close the websocket connection"""
        if self.ws:
            try:
                logger.info("Disconnecting from Smart Home...")
                self.ws.close()
                logger.success("Successfully disconnected from Smart Home")
            except Exception as e:
                logger.error(f"Error disconnecting from Smart Home: {str(e)}")
            finally:
                self.ws = None

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.disconnect()

    def get_next_id(self):
        self.nextId += 1
        return self.nextId

    @retry_on_websocket_error()
    def get_states(self, payload):
        logger.info('Getting available states...')
        payload["id"] = self.get_next_id()
        payload["type"] = "get_states"

        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())

        available_states = []
        for entity in response['result']:
            available_states.append(entity)

        logger.success(f'Successfully retrieved {len(available_states)} available states.')
        return Response.success(available_states)

    @retry_on_websocket_error()
    def get_services(self, payload):
        logger.info('Getting all available service actions...')
        payload["id"] = self.get_next_id()
        payload["type"] = "get_services"
        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())
        domains = {}
        for domain, services in response['result'].items():
            domains[domain] = services
        logger.success(f'Successfully retrieved {len(domains)} service actions.')
        return Response.success(domains)

    @retry_on_websocket_error()
    def call_service(self, payload):
        logger.info('Calling service...')
        payload["id"] = self.get_next_id()
        payload["type"] = "call_service"
        self.ws.send(json.dumps(payload))
        response = self.ws.recv()
        logger.success(f'Service called successfully. {response}')
        return Response.success(response)

    @retry_on_websocket_error()
    def light_on(self, lightId):
        logger.info(f'Turning light {lightId} on...')
        payload = {
            "id": self.get_next_id(),
            "type": "call_service",
            "domain": "light",
            "service": "turn_on",
            "target": {
                "entity_id": lightId
            },
        }

        self.ws.send(json.dumps(payload))
        response = self.ws.recv()
        logger.success(f'Light {lightId} turned on successfully. {response}')
        return Response.success(response)

    @retry_on_websocket_error()
    def light_off(self, lightId):
        logger.info(f'Turning light {lightId} off...')
        payload = {
            "id": self.get_next_id(),
            "type": "call_service",
            "domain": "light",
            "service": "turn_off",
            "target": {
                "entity_id": lightId
            },
        }

        self.ws.send(json.dumps(payload))
        response = self.ws.recv()
        logger.success(f'Light {lightId} turned off successfully. {response}')
        return Response.success(response)