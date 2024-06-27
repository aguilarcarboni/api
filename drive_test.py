from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_drive_api_helpers import queryForFile

SCOPES = ['https://www.googleapis.com/auth/drive']


creds = Credentials.from_authorized_user_file("creds/GoogleAuthedToken.json", SCOPES)
service = build('drive', 'v3', creds)

# Athena input
path1 = 'statements'
file_name = '062024.csv'

current_path = ''
path = path1 + '/' + file_name
paths = path.split('/')

for path in paths:
  try:
    files = queryForFile(path, creds)
    current_path += '/' + path
    print(files[0]['id'], current_path)
  except:
    print('Not found.')
    break