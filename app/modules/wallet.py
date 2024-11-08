from app.helpers.logger import logger
import requests as rq
import pandas as pd
import csv
from datetime import datetime

import requests as rq
import xml.etree.ElementTree as ET
import time
import pandas as pd
import csv

from app.helpers.response import Response

import os
from dotenv import load_dotenv

load_dotenv()

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

class BAC:

    def __init__(self):
        logger.announcement("Initializing BAC Wallet Service", type='info')
        self.accounts = [
            {
                'name':'Cash',
                'account_id':'CR83010200009295665295'
            }
        ]
        logger.announcement("Successfully initialized BAC Wallet Service", type='success')

    def generateStatements(self, account, month):

        logger.info(f"Generating statements for account: {account}, month: {month}")

        # Change path to account

        # TODO SHOULD I USE API OR DRIVE 
        path = 'Personal/Wallet/Statements/BAC/' +  account + '/Sources'
        dictToSend = {'path':path, 'file_name':month + '.csv'}

        logger.warning(f"Fix this. Line 41, Wallet.py.")
        response = rq.post(os.getenv('API_URL') + '/drive/download_file', json=dictToSend)

        if (response['status'] != 'success'):
            return Response.error('Error downloading file.')

        # Download file in plain text
        binaryFile = response.content
        file_text = binaryFile.decode('latin1')

        # Parse statements
        df_statements, account_number = self.parseStatements(file_text)

        # Validate account
        accounts = [{'id':'CR83010200009295665295', 'name':'Cash'}]
        account_number = account_number.strip()
        for acct in accounts:
            if acct['id'] == account_number and acct['name'] == account:
                acct = acct['name']

        # Get debits and credits
        df_debits, df_credits = self.getEntries(df_statements)

        # Categorize entries
        df_debits = self.categorizeStatements(df_debits)
        df_credits = self.categorizeStatements(df_credits)

        # Post process data
        df_all = pd.concat([df_debits, df_credits])
        df_all['Total'] = df_all['Credit'].astype(float) - df_all['Debit'].astype(float)
        df_all = df_all.sort_values(by='Date')

        # Save to drive as Bytes IO or save cache?
        drivePath = f'Personal/Wallet/Statements/BAC/{account}'
        cachePath = f'cache/statements/processed/{month}.csv'

        # Find processed folder
        logger.warning(f"Fix this. Line 78, Wallet.py.")
        response = rq.post('http://127.0.0.1:5001' + '/drive/query_file', json={'path':drivePath, 'file_name':'Processed'})
        if response.status_code != 200:
            raise Exception('Error querying Processed folder.')
        
        processed_folder_id = response.json()['content']['id']

        # Save file to cache
        try:
            df_all.to_csv(cachePath, index=False)
            logger.success(f"Successfully saved file {drivePath}/Processed/{month}.csv")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return Response.error('Error saving file.')
        
        # Upload file to drive
        try:
            logger.warning(f"Fix this. Line 95, Wallet.py.")
            response = rq.post('http://127.0.0.1:5001' + '/drive/upload_file_with_path', json={'file_path':cachePath, 'parent_folder_id':processed_folder_id})
            if response.status_code != 200:
                raise Exception('Error uploading file.')
            logger.success(f"Successfully saved file {drivePath}/Processed/{month}.csv")
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return Response.error('Error uploading file.')
        
        return Response.success(f'Successfully processed {month} financial statements for account: {account}. Saved to {drivePath}/Processed/{month}.csv')

    def parseStatements(self, file_text):

        logger.info("Parsing statements")
        rows = file_text.splitlines()
        parsed_csv = csv.reader(rows)
        account_number = None

        rows = []

        write = False
        previous_row = None
        
        for row in parsed_csv:
            if len(row) >  0:

                if previous_row is not None and len(previous_row) > 0 and previous_row[0] == 'Fecha de Transacción':
                    write = True

                if row[0] == '':
                    write = False
                
                if (write):
                    rows.append(row)

                if row[0].isdigit():
                    account_number = row[2]

            previous_row = row
            
        data = []
        for row in rows:
            try:
                date = datetime.strptime(row[0], '%d/%m/%Y')
            except:
                date = datetime.strptime(row[0], '%d/%m/%y')
                
            transaction = {'Date':date, 'Reference':row[1], 'Code':row[2], 'Description':row[3], 'Debit':row[4], 'Credit':row[5], 'Balance':row[6], 'Category':'', 'Q': 'Q1' if date.day < 15 else 'Q2'}
            data.append(transaction)

        df_statements = pd.DataFrame(data)
        df_statements['Date'] = pd.to_datetime(df_statements['Date'], format='%d/%m/%Y')

        logger.success("Successfully parsed statements.")

        return df_statements, account_number

    def getEntries(self, df_statements):
        logger.info("Getting entries from statements")
        df_debits = df_statements[df_statements['Credit'].astype(float) == 0].copy()
        logger.info("Successfully got debits.")
        df_credits = df_statements[df_statements['Debit'].astype(float) == 0].copy()
        logger.success("Successfully got credits.")
        return df_debits, df_credits
    
    def categorizeStatements(self, df_statements):
        logger.info("Categorizing statements")

        # Debits
        if len(df_statements[df_statements['Debit'].astype(float) == 0]) == 0:
        
            for index, row in df_statements.iterrows():

                for subscription in ['COMPA', 'SEGURO BELD', 'COMPASS']:
                    if subscription in row['Description']:
                        df_statements.loc[index, 'Category'] = 'Subscriptions'

                # Categorize income
                for gas_station in ['DELTA', 'SERVICIO', 'SERVICENTRO', 'GAS', 'Uber Rides']:
                    if gas_station in row['Description']:
                        df_statements.loc[index,'Category'] = 'Transportation'

                for savings_account in ['960587293', 'SAVINGS']:
                    if savings_account in row['Description']:
                        df_statements.loc[index,'Category'] = 'Savings'
            
            logger.success("Successfully categorized debits.")

        # Credits             
        else:

            for index, row in df_statements.iterrows():

                for savings_account in ['960587293', 'SAVINGS']:
                    if savings_account in row['Description']:
                        df_statements.loc[index,'Category'] = 'Savings'

                for income_source in ['DEP', '1Q', '2Q', 'INCOME']:
                    if income_source in row['Description']:
                        df_statements.loc[index,'Category'] = 'Income'
            
            logger.success("Successfully categorized credits.")

        return df_statements

    def manuallyCategorizeStatements(self, df_statements):
        for index, row in df_statements[df_statements['Category'] == ''].iterrows():
            category = input('Enter category for statement:')
            df_statements.loc[index, 'Category'] = category

        return df_statements
