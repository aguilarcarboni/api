from app.helpers.logger import logger
import requests as rq
import pandas as pd
import csv
from datetime import datetime

from app.helpers.response import Response

import os
from dotenv import load_dotenv

load_dotenv()

logger.announcement('Initializing Wallet', 'info')
logger.announcement('Successfully initialized Wallet', 'success')

# TODO FIX DRIVE MIGRATION

class BAC:

    def __init__(self):
        logger.info("Initializing BAC")
        self.accounts = [
            {
                'name':'Cash',
                'account_id':'CR83010200009295665295'
            }
        ]
        logger.success("Successfully initialized BAC")

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
