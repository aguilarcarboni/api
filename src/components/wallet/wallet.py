from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os

from src.utils.logger import logger

logger.announcement('Initializing Wallet Service', 'info')

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'wallet.db')
db_url = f'sqlite:///{db_path}'
engine = create_engine(db_url)

Base = declarative_base()

class Account(Base):
    """Account table"""
    __tablename__ = 'account'
    id = Column(String, primary_key=True, unique=True)
    name = Column(String)
    drive_source_id = Column(String)
    updated = Column(String)
    created = Column(String)

class Expense(Base):
    """Expense table"""
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String)
    date = Column(String)
    code = Column(String)
    description = Column(String)
    category = Column(String)
    balance = Column(Float, unique=True)
    debit = Column(Float)
    credit = Column(Float)
    total = Column(Float)
    account_id = Column(String)
    updated = Column(String)
    created = Column(String)

class Category(Base):
    """Category table"""
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String)
    amount = Column(Float)
    updated = Column(String)
    created = Column(String)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

"""
# Create Accounts
logger.info('Populating accounts...')
db.create('account', {'name': 'BAC Cash', 'id': 'CR83010200009295665295', 'drive_source_id': '15J8BHOj73Au9Fk6yN0oVu2rm79ccEHf7'})

# Create Categories
logger.info('Populating categories for budget...')
categories = [
    {'id': 1, 'name': 'Food', 'type': 'expense', 'amount': 45000},
    {'id': 2, 'name': 'Transportation', 'type': 'expense', 'amount': 35000},
    {'id': 3, 'name': 'Recreation', 'type': 'expense', 'amount': 60000},
    {'id': 4, 'name': 'Savings', 'type': 'expense', 'amount': 80000},
    {'id': 5, 'name': 'Subscriptions', 'type': 'expense', 'amount': 25000},
    {'id': 6, 'name': 'Personal Care', 'type': 'expense', 'amount': 25000},
    {'id': 7, 'name': 'Salary', 'type': 'income', 'amount': 270000},
    {'id': 8, 'name': 'Freelance', 'type': 'income', 'amount': 0},
    {'id': 9, 'name': 'Investments', 'type': 'income', 'amount': 0},
    {'id': 10, 'name': 'Savings', 'type': 'income', 'amount': 0},
]

for category in categories:
    db.create('category', category)

logger.announcement("Successfully initialized Wallet Service", type='success')
"""