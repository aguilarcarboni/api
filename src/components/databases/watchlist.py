from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os
from src.utils.logger import logger

Base = declarative_base()

class Movies(Base):
    """Movies table"""
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    director = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    notes = Column(String)
    updated = Column(String)
    created = Column(String)

class Shows(Base):
    """Shows table"""
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    director = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    notes = Column(String)
    updated = Column(String)
    created = Column(String)

logger.announcement('Initializing Watchlist Service', 'info')

db_name = 'watchlist'
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', f'{db_name}.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

logger.announcement('Successfully initialized Watchlist Service', 'success')
