
import pandas as pd
import csv
from datetime import datetime
import pandas as pd
import csv

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os

from src.utils.logger import logger

logger.announcement('Initializing Bank Statements Service', 'info')
Base = declarative_base()

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

db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'db', 'statements.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)
db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

#db.create('account', {'name': 'BAC', 'account_id': '1234567890', 'drive_source_id': '1234567890'})

logger.announcement("Successfully initialized Bank Statements Service", type='success')
