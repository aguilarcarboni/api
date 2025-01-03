from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os

from src.utils.logger import logger

logger.announcement('Initializing Wallet Statements Service', 'info')
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
    category_id = Column(Integer)
    balance = Column(Float)
    debit = Column(Float)
    credit = Column(Float)
    total = Column(Float)
    account_id = Column(String)
    updated = Column(String)
    created = Column(String)

class ExpenseCategory(Base):
    """ExpenseCategory table"""
    __tablename__ = 'expense_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    updated = Column(String)
    created = Column(String)

class Category(Base):
    """Category table"""
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String)
    updated = Column(String)
    created = Column(String)

class Budget(Base):
    """Budget table"""
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer)
    amount = Column(Float)
    updated = Column(String)
    created = Column(String)

db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'wallet.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)
db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

db.create('account', {'name': 'BAC Cash', 'id': 'CR83010200009295665295', 'drive_source_id': '15J8BHOj73Au9Fk6yN0oVu2rm79ccEHf7'})

logger.announcement("Successfully initialized Bank Statements Service", type='success')
