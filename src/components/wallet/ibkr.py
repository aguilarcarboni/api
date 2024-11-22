import requests as rq
import xml.etree.ElementTree as ET
import csv
import pandas as pd
import time

from src.utils.logger import logger
from src.utils.response import Response

class IBKR:

    def __init__(self):
        logger.announcement("Initializing IBKR Wallet Service", type='info')

        logger.info('Initializing Flex Query Service')
        self.version = '&v=3'
        self.url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/SendRequest?"
        logger.success('Initialized Flex Query Service')

        logger.announcement("Successfully initialized IBKR Wallet Service", type='success')

    # Returns flex query as df (internal use only)
    def getFlexQuery(self, token, queryId):

        logger.info(f'Getting Flex Query for queryId: {queryId}')

        try:

            xml_data = None

            retry_count = 0
            max_retries = 5
            retry_delay = 1
            
            # Create url for GET request to API for generating a report
            logger.info('Requesting Flex Query Template...')
            generatedTemplateURL = "".join([self.url, token, '&q=' + queryId, self.version])
            generatedTemplateResponse = rq.get(url=generatedTemplateURL)
            while generatedTemplateResponse.status_code != 200 and retry_count < max_retries:
                logger.warning(f'Flex Query Template Generation Failed. Preview: {generatedTemplateResponse.text[0:100]}')
                logger.info(f'Retrying... Attempt {retry_count} of {max_retries}')
                time.sleep(retry_delay)
                generatedTemplateResponse = rq.get(url=generatedTemplateURL)
                retry_count += 1

            logger.success('Flex Query Template Generated')

            # Populate ET element with generated report template
            tree = ET.ElementTree(ET.fromstring(generatedTemplateResponse.content))
            root = tree.getroot()
            refCode = "&q=%s" % root.find('ReferenceCode').text

            # Create url for GET request to API to fetch generated report
            logger.info("Generating Flex Query...")
            generatedReportURL = root.find('Url').text
            generatedReportURL = "".join([generatedReportURL, "?",token, refCode, self.version])
            generatedReportResponse = rq.get(url=generatedReportURL, allow_redirects=True)
            while generatedReportResponse.status_code != 200 and retry_count < max_retries:
                logger.warning(f'Flex Query Generation Failed. Preview: {generatedReportResponse.text[0:100]}')
                logger.info(f'Retrying... Attempt {retry_count} of {max_retries}')
                time.sleep(retry_delay)
                generatedReportResponse = rq.get(url=generatedReportURL, allow_redirects=True)
                retry_count += 1
            
            xml_data = generatedReportResponse.content
            df = self.binaryXMLtoDF(xml_data)

            logger.success(f"Flex Query generated")
            return Response.success(df)
        
        except Exception as e:

            logger.error(f"Error: {str(e)}")
            return Response.error(f"Failed to get Flex Query: {str(e)}")

    # Returns dict of queryIds as keys and flex query as values
    def fetchFlexQueries(self,queryIds):
        try:

            agmToken = "t=949768708375319238802665"
            flex_queries = {}

            for _, queryId in enumerate(queryIds):
                flex_query_df = None
                response = self.getFlexQuery(agmToken, queryId)
                if response['status'] == 'error':
                    return Response.error(f'Error fetching Flex Query for queryId {queryId}.')
                
                flex_query_df = response['content']
                flex_query_df['file_name'] = queryId

                try:
                    flex_query_dict = flex_query_df.to_dict(orient='records')
                    flex_queries[queryId] = flex_query_dict
                except:
                    logger.error(f'Flex Query Empty for queryId {queryId}')
                    return Response.error(f'Flex Query Empty for queryId {queryId}')
            return Response.success(flex_queries)
        
        except Exception as e:
            logger.error(f'Error fetching Flex Queries: {str(e)}')
            return Response.error(f'Error fetching Flex Queries: {str(e)}')

    def binaryXMLtoCSV(self, binaryXMLData, file_name):
        logger.info(f'Converting binary XML to CSV for file: {file_name}')
        try:
            xml_data = binaryXMLData.decode('utf-8')
            reader = csv.reader(xml_data.splitlines(), skipinitialspace=True)

            with open('backups/acobo/' + file_name + '.csv',  'w', encoding='utf-8') as out_file:
                writer = csv.writer(out_file)
                for row in reader:
                    if ('BOA' not in row) and ('BOF' not in row) and ('BOS' not in row) and ('EOS' not in row) and ('EOA' not in row) and ('EOF' not in row):
                        writer.writerow(row)

            logger.success(f'Successfully converted binary XML to CSV for file: {file_name}')
            return Response.success('backups/acobo/' + file_name + '.csv')
        except Exception as e:
            logger.error(f"Error in binaryXMLtoCSV: {str(e)}")
            return Response.error(f"Failed to convert binary XML to CSV: {str(e)}")

    def binaryXMLtoDF(self, binaryXMLData):

        logger.info(f'Converting binary XML to DF')
        try:
            xml_data = binaryXMLData.decode('utf-8')
            reader = csv.reader(xml_data.splitlines(), skipinitialspace=True)

            rows = []

            for row in reader:
                if ('BOA' not in row) and ('BOF' not in row) and ('BOS' not in row) and ('EOS' not in row) and ('EOA' not in row) and ('EOF' not in row) and ('MSG' not in row):
                    rows.append(row)
            
            df = pd.DataFrame(rows[1:], columns=rows[0])
            logger.success(f'Successfully converted binary XML to DF')
            return df
        
        except Exception as e:
            logger.error(f"Error. Failed to convert binary XML to DF: {str(e)}")
            return Response.error(f"Failed to convert binary XML to DF: {str(e)}")
