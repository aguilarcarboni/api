
import pandas as pd
import csv
from datetime import datetime
import pandas as pd
import csv

from src.components.wallet.statements.statements import db

from src.utils.response import Response
from src.utils.api import access_api
from src.utils.logger import logger

"""
Generates expense statements for a given account and month.
Saves expense statements to drive and database.
"""
def generateStatements(account, month):

    logger.announcement(f"Generating statements for account: {account}, month: {month}", 'info')

    # Download source file from drive
    # Must be downloaded from BAC account
    response = db.read('account', {'name': account})
    accounts = response['content']

    if len(accounts) != 1:
        logger.error(f"Error finding account: {accounts}")
        return Response.error('Error finding account.')
    
    account_id = accounts[0]['drive_source_id']

    response = access_api('/drive/get_file_info', 'POST', {'file_name':f'{month}.csv', 'parent_id':account_id})
    file_id = response['content']['id']
    response = access_api('/drive/download_file', 'POST', {'file_id':file_id})
    
    try:
        file_text = response.decode('latin1')
    except Exception as e:
        logger.error(f"Error decoding file: {str(e)}")
        return Response.error('Error decoding file.')

    df_statements, account_number = parseStatements(file_text)

    logger.announcement(f"Identified account number: {account_number}, verifying account...", 'info')

    response = db.read('account')
    accounts = response['content']

    if len(accounts) == 0:
        return Response.error('No accounts found.')

    verified = False
    for acct in accounts:
        if acct['account_id'] == account_number and acct['name'] == account:
            logger.announcement(f"Account verified: {acct}", 'success')
            verified = True

    if not verified:
        logger.error(f"Account not found: {account_number} {account}")
        return Response.error('Account not found.')

    # Extract debits and credits
    df_debits, df_credits = getEntries(df_statements)

    # Categorize entries
    df_debits = categorizeStatements(df_debits)
    df_credits = categorizeStatements(df_credits)

    # Post process data
    df_all = pd.concat([df_debits, df_credits])
    df_all['Balance'] = df_all['Balance'].astype(float)
    df_all['Debit'] = df_all['Debit'].astype(float)
    df_all['Credit'] = df_all['Credit'].astype(float)
    df_all['Total'] = df_all['Credit'] - df_all['Debit']
    df_all = df_all.sort_values(by='Date')

    # Save file to cache for quicker access
    # TODO: Save to cluster instead?
    # TODO: Use redis or remove cache?
    
    # Save to database
    num_saved = 0
    expenses_dict = df_all.to_dict(orient='records')
    for expense in expenses_dict:

        # Transform keys to lowercase to match column names
        expense_transformed = {
            'Date': str(expense['Date']),
            'Reference': expense['Reference'],
            'Code': expense['Code'],
            'Description': expense['Description'],
            'Category': expense['Category'],
            'Balance': expense['Balance'],
            'Debit': expense['Debit'],
            'Credit': expense['Credit'],
            'Total': expense['Total']
        }
        logger.info(f"Saving expense: {expense_transformed}")
        try:
            db.create('expense', expense_transformed)
            num_saved += 1
        except Exception as e:
            logger.error(f"Error saving expense: {str(e)}")
            return Response.error('Error saving expense.')
        
    logger.announcement(f"Successfully saved {num_saved}/{len(expenses_dict)} expenses to database.", 'success')
    return Response.success(f'Successfully processed {month} financial statements for account: {account}.')

def parseStatements(file_text):

    logger.info("Parsing expense statements")
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

            if row[0] == '' or 'Resumen de Estado Bancario' in row[0]:
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
            
        transaction = {'Date':date, 'Reference':row[1], 'Code':row[2], 'Description':row[3], 'Debit':row[4], 'Credit':row[5], 'Balance':row[6], 'Category':''}
        data.append(transaction)

    df_statements = pd.DataFrame(data)
    df_statements['Date'] = pd.to_datetime(df_statements['Date'], format='%d/%m/%Y')

    logger.success(f"Successfully parsed {len(df_statements)} statements")

    return df_statements, account_number.strip()

def getEntries(df_statements):
    logger.info("Getting entries from statements")
    df_debits = df_statements[df_statements['Credit'].astype(float) == 0].copy()
    logger.info("Successfully got debits.")
    df_credits = df_statements[df_statements['Debit'].astype(float) == 0].copy()
    logger.success("Successfully got credits.")
    return df_debits, df_credits

def categorizeStatements(df_statements):
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

def manuallyCategorizeStatements(df_statements):
    for index, row in df_statements[df_statements['Category'] == ''].iterrows():
        category = input('Enter category for statement:')
        df_statements.loc[index, 'Category'] = category

    return df_statements

