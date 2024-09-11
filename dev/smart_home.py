import requests as rq
import json


response = rq.get("http://192.168.0.13:5001/home/get_services")
content_dict = json.loads(response.json()['content'])
print(content_dict['result'])

for entity in content_dict['result']:
    print(entity, '\n')
