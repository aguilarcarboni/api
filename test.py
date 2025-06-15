import requests

response = requests.post("http://localhost:5000/token", verify=False, json={"token": "admin", "scopes": "all"})

summary = requests.get("http://localhost:5000/account/summary", verify=False, headers={"Authorization": f"Bearer {response.json()['access_token']}"})
print("Summary:")
print(summary.json())

positions = requests.get("http://localhost:5000/account/positions", verify=False, headers={"Authorization": f"Bearer {response.json()['access_token']}"})
print("Positions:")
print(positions.json())

open_orders = requests.get("http://localhost:5000/orders/open-orders", verify=False, headers={"Authorization": f"Bearer {response.json()['access_token']}"})
print("Open Orders:")
print(open_orders.json())

completed_orders = requests.get("http://localhost:5000/orders/completed-orders", verify=False, headers={"Authorization": f"Bearer {response.json()['access_token']}"})
print("Completed Orders:")
print(completed_orders.json())