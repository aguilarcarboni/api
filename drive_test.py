import os
from googleapiclient.discovery import build

service = build('drive', 'v3')

path_athena = '/content/gdrive/MyDrive/Athena/'

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