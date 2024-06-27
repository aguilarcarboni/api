
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

uri = "mongodb+srv://aguilarcarboni:NewYork2020@athena.jcntnxw.mongodb.net/?retryWrites=true&w=majority&appName=Athena"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
print('Initialized client')

# Send a ping to confirm a successful connection
try:
    db = client['main']

    path = 'profiles'
    query = {
      "name": "Andres",
      "status": {"$regex": "o", "$options": "i"}
    }

    paths = path.split('/')
    
    profiles = db[paths[0]]
    profile = profiles.find_one(query)
    print(profile)

except Exception as e:
    print(e)

"""
# Athena input
path = 'statements/'
file_name = '062024.csv'

current_path = ''

paths = path.split('/')
found = False
for path in paths:

  files = os.listdir(path_athena + current_path)
  for f in files:
    if f == file_name:
      found = True
      break

    if f == path:
      current_path += path + '/'

if found:
  print(f'Found. Path: {path_athena + current_path + file_name}')
else:
  print('Not found.')
"""