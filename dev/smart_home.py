import requests as rq
import json

import time

sleep_time = 5

# Get all domains and their services
response = rq.post("http://192.168.0.13:5001/home/get_services", json={})
print(response.json())

# Get all devices
response = rq.post("http://192.168.0.13:5001/home/get_states", json={})
print(response.json()['content'])

time.sleep(sleep_time)
print('-'*10)

domain = 'light'
service = 'turn_on'
device = 'office_ceiling'

# Show attributes for a device
print('Attributes:')
response = rq.post("http://192.168.0.13:5001/home/get_states", json={})
content_dict = json.loads(response.json()['content'])
for entity in content_dict['result']:
    if entity['entity_id'] == f'{domain}.{device}':
        #print(entity)
        for attribute in entity['attributes'].items():
            print(attribute)
        print('State:', entity['state'])

time.sleep(sleep_time)
print('-'*10)

print('Available fields:')
# Show all available fields for a specific domain and service
response = rq.post("http://192.168.0.13:5001/home/get_services", json={})
content_dict = json.loads(response.json()['content'])
for entity in content_dict['result'][domain][service]['fields'].items():
    print(entity, '\n')

time.sleep(sleep_time)

# Call a specific service on a specific device with specific service data selected from the available fields

payload = {
    "domain": domain,
    "service": service,
    "service_data": {
    },
    "target": {
        "entity_id": f'{domain}.{device}'
    }
}

print('Turning on gaming mode...')
response = rq.post("http://192.168.0.13:5001/home/call_service", json=payload)
content_dict = json.loads(response.json()['content'])

time.sleep(2)