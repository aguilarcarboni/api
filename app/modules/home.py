from app.helpers.logger import logger
from app.helpers.response import Response
import requests
import json
from websocket import create_connection
import os

class SmartHome:

    def __init__(self):
        logger.announcement('Initializing Smart Home', 'info')
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3YmM2MzI5NTQzYmQ0MmUyODgwMmNlNzg3ZDFlOWQyMCIsImlhdCI6MTczMTA5NjAyNSwiZXhwIjoyMDQ2NDU2MDI1fQ.GWsuI1GuIbg96XKMrATg2pAO8sNk_r94GWIKHiaOElw"
        self.ws = None
        self.nextId = 0
        self.connect()

    def connect(self):
        """Establish websocket connection and authenticate"""
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

    def getNextId(self):
        self.nextId += 1
        return self.nextId

    def get_states(self, payload):
        
        logger.info('Getting available states...')
        payload["id"] = self.getNextId()
        payload["type"] = "get_states"

        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())

        available_states = []
        for entity in response['result']:
            available_states.append(entity)

        logger.success(f'Successfully retrieved {len(available_states)} available states.')
        return Response.success(available_states)

    def get_services(self, payload):
        logger.info('Getting all available service actions...')
        payload["id"] = self.getNextId()
        payload["type"] = "get_services"
        self.ws.send(json.dumps(payload))
        response = json.loads(self.ws.recv())
        domains = {}
        for domain, services in response['result'].items():
            domains[domain] = services
        logger.success(f'Successfully retrieved {len(domains)} service actions.')
        return Response.success(domains)

    def call_service(self, payload):
        logger.info('Calling service...')
        payload["id"] = self.getNextId()
        payload["type"] = "call_service"
        self.ws.send(json.dumps(payload))
        response = self.ws.recv()
        logger.success(f'Service called successfully. {response}')
        return Response.success(response)

    def light_on(self, lightId):

        logger.info(f'Turning light {lightId} on...')
        payload = {
            "id": self.getNextId(),
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

    def light_off(self, lightId):
        logger.info(f'Turning light {lightId} off...')
        payload = {
        "id": self.getNextId(),
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

    def refresh_tv():

        logger.announcement('Refreshing TV playlist...', 'info')
        
        url = "http://xdplayer.tv:8080"
        username = "aguilarcarboni"
        password = "pXU2Hx6NMu"
        get_all_streams = f"/get.php?username={username}&password={password}&type=m3u_plus&output=ts"

        logger.info('Fetching playlist...')
        response = requests.get(url + get_all_streams)
        if response.status_code != 200:
            logger.error(f'Failed to fetch playlist: {response.status_code}')
            return Response.error(f'Failed to fetch playlist: {response.status_code}')
        logger.success('Playlist fetched successfully')

        # Save the first 2000 lines of the m3u file
        logger.info('Saving playlist...')
        with open('/Users/andres/Documents/Projects/Laserfocus/laserfocus-api/cache/tv/playlist.m3u', 'w', encoding='utf-8') as f:
            lines = response.text.splitlines()
            for i, line in enumerate(lines[:int(2000)]):
                if i % 100 == 0:
                    logger.info(f'Writing {i}/{len(lines)} lines...')
                f.write(line + '\n')

        logger.announcement('Playlist saved successfully', 'success')
        return Response.success('Playlist saved successfully')