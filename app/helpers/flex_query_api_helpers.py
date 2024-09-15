import requests as rq
import xml.etree.ElementTree as ET
import time
import pandas as pd
import csv
from datetime import datetime

def getFlexQuery(token, queryId):

  version='&v=3'

  url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/SendRequest?"

  # Crete url for GET request to API for generating a report
  generatedTemplateURL = "".join([url, token, '&q=' + queryId, version])

  # Make a GET request to the API
  generatedTemplateResponse = rq.get(url=generatedTemplateURL)

  # If the request was not successful:
  if generatedTemplateResponse.status_code != 200:
    print("Error!", generatedTemplateResponse.status_code)
    exit()

  # Populate ET element with generated report template!!
  tree = ET.ElementTree(ET.fromstring(generatedTemplateResponse.content))
  root = tree.getroot()

  # Find reference code of generated report
  refCode = "&q=%s" % root.find('ReferenceCode').text

  # Create url for GET request to API to fecth generated report
  generatedReportURL = root.find('Url').text
  generatedReportURL = "".join([generatedReportURL, "?",token, refCode, version])

  # Wait for generation to finish
  print("Generating Flex Query...")
  for i in range(60,0,-1):
    time.sleep(1)
    if i % 10 == 0:
        print('Waiting for', i, 'second(s)')

  # Make a GET request to the API for fetching the generated report
  generatedReportResponse = rq.get(url=generatedReportURL, allow_redirects=True)
  xml_data = generatedReportResponse.content

  print("Flex Query generated.")

  # Create a CSV file backup of the Flex Query
  now = datetime.now()
  now = now.strftime('%Y%m%d%H%M%S')

  csv_file_path = binaryXMLtoCSV(xml_data, queryId)

  df = pd.read_csv(csv_file_path)

  return df

def binaryXMLtoCSV(binaryXMLData, file_name):

    xml_data = binaryXMLData.decode('ascii')
    reader = csv.reader(xml_data.splitlines(), skipinitialspace=True)

    with open('csv/' + file_name + '.csv',  'w') as out_file:
        writer = csv.writer(out_file)
        for row in reader:
          if ('BOA' not in row) and ('BOF' not in row) and ('BOS' not in row) and ('EOS' not in row) and ('EOA' not in row) and ('EOF' not in row):
            writer.writerow(row)

    return 'csv/' + file_name + '.csv'