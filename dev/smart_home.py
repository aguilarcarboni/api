import requests as rq
import json

import time

sleep_time = 0.5

# Get all domains and their services
response = rq.post("http://192.168.0.13:5001/home/get_services", json={})
for domain, services in response.json()['content'].items():
    print(domain, services, 'n')

# Get all devices
response = rq.post("http://192.168.0.13:5001/home/get_states", json={})
for device in response.json()['content']:
    print('device:', device, '\n')

time.sleep(sleep_time)
print('-'*10)

domain = 'scene'
service = 'turn_on'
device = 'office_work'

time.sleep(sleep_time)
print('-'*10)

time.sleep(sleep_time)

# Call a specific service on a specific device with specific service data selected from the available fields
payload = {
    "domain": domain,
    "service": service,
    "service_data": {
    },
    "target": {
        "entity_id": f'{domain}.{device}_2'
    }
}

response = rq.post("http://192.168.0.13:5001/home/call_service", json=payload)
content_dict = json.loads(response.json()['content'])