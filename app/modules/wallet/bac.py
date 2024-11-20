from app.helpers.logger import logger
import pandas as pd
import csv
from datetime import datetime
import pandas as pd
import csv
from app.helpers.response import Response
from app.helpers.api import access_api

from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import os

from app.helpers.logger import logger
from app.helpers.response import Response

from functools import wraps

Base = declarative_base()

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session(bind=engine)
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            return Response.error(f"Database error: {str(e)}")
        finally:
            session.close()
    return wrapper

@with_session
def create(session, table: str, data: dict):
    logger.info(f'Attempting to create new entry in table: {table}')

    try:
        tbl = Table(table, metadata, autoload_with=engine)
        new_record = tbl.insert().values(**data)
        result = session.execute(new_record)
        session.flush()
        new_id = result.inserted_primary_key[0]
        logger.success(f'Successfully created entry with id: {new_id}')
        return Response.success({'id': new_id })
    except SQLAlchemyError as e:
        logger.error(f'Error creating record: {str(e)}')
        return Response.error(f'Database error: {str(e)}')

@with_session
def update(session, table: str, params: dict, data: dict):
    logger.info(f'Attempting to update entry in table: {table}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        for key, value in params.items():
            if hasattr(tbl.c, key):
                query = query.filter(getattr(tbl.c, key) == value)

        item = query.first()

        if not item:
            return Response.error(f"Bills with given parameters not found")

        query.update(data)
        session.flush()

        updated_item = query.first()
        logger.success(f"Successfully updated {table} with new data {updated_item._asdict()}")
        return Response.success(f"Successfully updated {table} with new data {updated_item._asdict()}")
    except SQLAlchemyError as e:
        logger.error(f"Error updating {table}: {str(e)}")
        raise

@with_session
def read(session, table: str, params: dict = None):
    logger.info(f'Attempting to read entry from table: {table}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        if params:
            for key, value in params.items():
                if hasattr(tbl.c, key):
                    query = query.filter(getattr(tbl.c, key) == value)
            
        results = query.all()

        serialized_results = [row._asdict() for row in results]
        
        logger.success(f'Successfully read {len(serialized_results)} entries from table: {table}')
        return Response.success(serialized_results)
    except SQLAlchemyError as e:
        logger.error(f'Error reading from database: {str(e)}')
        raise

@with_session
def delete(session, table: str, params: dict):
    logger.info(f'Attempting to delete entry from table: {table}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        for key, value in params.items():
            if hasattr(tbl.c, key):
                query = query.filter(getattr(tbl.c, key) == value)

        item = query.first()
        if not item:
            return Response.error(f"{table} with given parameters not found")

        delete_stmt = tbl.delete().where(tbl.c.id == item.id)
        session.execute(delete_stmt)
        session.flush()

        logger.success(f"Successfully deleted {table} with id: {item.id}")
        return Response.success(f"{table} deleted successfully")
    
    except SQLAlchemyError as e:
        logger.error(f"Error deleting {table}: {str(e)}")
        raise

logger.announcement('Initializing BAC Database Service', 'info')

class Expense(Base):
    """Expense table"""
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Reference = Column(String)
    Date = Column(String)
    Code = Column(String)
    Description = Column(String)
    Category = Column(String)
    Balance = Column(Float)
    Debit = Column(Float)
    Credit = Column(Float)
    Total = Column(Float)

class Account(Base):
    """Account table"""
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, unique=True)
    name = Column(String)
    drive_source_id = Column(String)

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'wallet', 'bac.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)
Base.metadata.create_all(engine)

metadata = MetaData()
metadata.reflect(bind=engine)

logger.announcement('BAC Database Service initialized', 'success')

class BAC:

    def __init__(self):
        logger.announcement("Initializing BAC Wallet Service", type='info')
        logger.announcement("Successfully initialized BAC Wallet Service", type='success')

    """
    Generates expense statements for a given account and month.
    Saves expense statements to drive and database.
    """
    def generateStatements(self, account, month):

        logger.announcement(f"Generating statements for account: {account}, month: {month}", 'info')

        # Download source file from drive
        # Must be downloaded from BAC account
        response = read('account', {'name': account})
        accounts = response['content']

        if len(accounts) != 1:
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

        df_statements, account_number = self.parseStatements(file_text)

        logger.announcement(f"Identified account number: {account_number}, verifying account...", 'info')

        response = read('account')
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
        df_debits, df_credits = self.getEntries(df_statements)

        # Categorize entries
        df_debits = self.categorizeStatements(df_debits)
        df_credits = self.categorizeStatements(df_credits)

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
                create('expense', expense_transformed)
                num_saved += 1
            except Exception as e:
                logger.error(f"Error saving expense: {str(e)}")
                return Response.error('Error saving expense.')
            
        logger.announcement(f"Successfully saved {num_saved}/{len(expenses_dict)} expenses to database.", 'success')
        return Response.success(f'Successfully processed {month} financial statements for account: {account}.')

    def parseStatements(self, file_text):

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
