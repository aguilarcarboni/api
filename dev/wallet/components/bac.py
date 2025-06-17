
import pandas as pd
import csv
from datetime import datetime
import pandas as pd
import csv

from src.components.wallet.wallet import db

from laserfocus.utils.response import Response
from src.utils.api import access_api
from laserfocus.utils.logger import logger

"""
Generates expense statements for a given account and month.
Saves expense statements to drive and database.
"""
def generateStatements(account, month):

    logger.announcement(f"Generating statements for account: {account}, month: {month}", 'info')

    # Delete all expenses for the current month
    db.delete_all('expense')

    # Get account from database
    response = db.read('account', {'id': account})
    accounts = response['content']

    if len(accounts) != 1:
        return Response.error('Error finding account. Review database.')
    
    account_drive_id = accounts[0]['drive_source_id']
    account_id = accounts[0]['id']

    logger.announcement("Downloading statements file...", 'info')

    # Download source file from drive
    response = access_api('/drive/get_file_info', 'POST', {'file_name':f'{month}.csv', 'parent_id':account_drive_id})
    if response['status'] != 'success':
        return Response.error('Failed to find statements file.')
    
    file_id = response['content']['id']
    response = access_api('/drive/download_file', 'POST', {'file_id':file_id})
    try:
        file_text = response.decode('latin1')
    except Exception as e:
        return Response.error(f'Error decoding file.')
    
    logger.announcement("Successfully downloaded statements file.", 'success')

    # Parse and process statements
    logger.announcement("Parsing statements...", 'info')
    df_statements, account_number = parseStatements(file_text)
    logger.announcement("Successfully parsed statements.", 'success')

    logger.announcement(f"Identified account number: {account_number}, verifying account...", 'info')

    verified = False
    for acct in accounts:
        if acct['id'] == account_number:
            logger.announcement(f"Account verified.", 'success')
            verified = True

    if not verified:
        logger.error(f"Account not found: {account_number} {account}")
        return Response.error('Account not found.')

    logger.announcement("Extracting debits and credits...", 'info')
    df_debits, df_credits = getEntries(df_statements)
    logger.announcement("Successfully extracted debits and credits.", 'success')

    
    logger.announcement("Categorizing entries...", 'info')
    df_debits = categorizeStatements(df_debits)
    df_credits = categorizeStatements(df_credits)
    logger.announcement("Successfully categorized entries.", 'success')
    

    # Post process data
    logger.announcement("Post processing data...", 'info')
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
            'date': str(expense['Date']),
            'reference': expense['Reference'],
            'code': expense['Code'],
            'description': expense['Description'],
            'category': expense['Category'],
            'balance': expense['Balance'],
            'debit': expense['Debit'],
            'credit': expense['Credit'],
            'total': expense['Total'],
            'account_id': account_id
        }
        try:
            db.create('expense', expense_transformed)
            num_saved += 1
        except Exception as e:
            logger.error(f"Error saving expense: {str(e)}")

    logger.announcement("Successfully post processed data.", 'success')
    
    logger.announcement(f"Successfully processed {month} financial statements for account: {account}.", 'success')
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

    # Debits/Expenses
    number_of_debits = len(df_statements[df_statements['Debit'].astype(float) == 0])

    if number_of_debits == 0:
    
        for index, row in df_statements.iterrows():

            for subscription in ['COMPA', 'SEGURO BELD', 'COMPASS']:
                if subscription in row['Description']:
                    category = db.read('category', {'name': 'Subscriptions', 'type': 'expense'})['content'][0]
                    df_statements.loc[index,'Category'] = category['name']

            # Categorize income
            for gas_station in ['DELTA', 'SERVICIO', 'SERVICENTRO', 'GAS', 'Uber Rides']:
                if gas_station in row['Description']:
                    category = db.read('category', {'name': 'Transportation', 'type': 'expense'})['content'][0]
                    df_statements.loc[index,'Category'] = category['name']

            for savings_account in ['960587293', 'SAVINGS']:
                if savings_account in row['Description']:
                    category = db.read('category', {'name': 'Savings', 'type': 'expense'})['content'][0]
                    df_statements.loc[index,'Category'] = category['name']

        logger.success("Successfully categorized debits.")

    # Credits/Incomes          
    else:

        for index, row in df_statements.iterrows():

            for savings_account in ['960587293', 'SAVINGS']:
                if savings_account in row['Description']:
                    category = db.read('category', {'name': 'Savings', 'type': 'income'})['content'][0]
                    df_statements.loc[index,'Category'] = category['name']

            for income_source in ['DEP', '1Q', '2Q', 'INCOME']:
                if income_source in row['Description']:
                    category = db.read('category', {'name': 'Salary', 'type': 'income'})['content'][0]
                    df_statements.loc[index,'Category'] = category['name']
        
        logger.success("Successfully categorized credits.")

    return df_statements
