from app.helpers.logger import logger
from app.helpers.response import Response

import json
from websocket import create_connection

logger.announcement('Initializing Smart Home', 'info')

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0NDhhOWQ2MDFkYzk0YzgxYWI3YThhNDQ1NzY3OGYwOCIsImlhdCI6MTcyNTczNjk4OSwiZXhwIjoyMDQxMDk2OTg5fQ.bepKyJyKb4mS5lbDzfXFRC25pk53oiChreza4rvL3q8"
try:
    ws = create_connection("ws://oasis.local:8123/api/websocket")
except:
    logger.error("Failed to initialize Smart Home.")
    exit()
nextId = 0
print(ws.recv())
ws.send(json.dumps({'type': 'auth', 'access_token': token}))
print(ws.recv())

logger.announcement("Successfully initialized Smart Home.", 'success')

def getNextId(self):
    self.nextId += 1
    return self.nextId

def get_states(self, payload):
    payload["id"] = self.getNextId()
    payload["type"] = "get_states"

    self.ws.send(json.dumps(payload))
    response = json.loads(self.ws.recv())

    devices = []
    for entity in response['result']:
        devices.append(entity)

    return Response.success(devices)

def get_services(self, payload):
    payload["id"] = self.getNextId()
    payload["type"] = "get_services"

    self.ws.send(json.dumps(payload))
    response = json.loads(self.ws.recv())
    domains = {}
    for domain, services in response['result'].items():
        domains[domain] = services
        
    return Response.success(domains)

def call_service(self, payload):
    payload["id"] = self.getNextId()
    payload["type"] = "call_service"

    self.ws.send(json.dumps(payload))
    return Response.success(self.ws.recv())

def light_on(self, lightId):
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
    return Response.success(self.ws.recv())

def light_off(self, lightId):
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
    return Response.success(self.ws.recv())
