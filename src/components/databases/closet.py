from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os
from src.utils.logger import logger

Base = declarative_base()

class Clothes(Base):
    """Movies table"""
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    color = Column(String)
    state = Column(String)
    type = Column(String)
    tags = Column(String)
    
logger.announcement('Initializing Closet Service', 'info')

db_name = 'closet'
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', f'{db_name}.db')
db_url = f'sqlite:///{db_path}'

engine = create_engine(db_url)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

logger.announcement('Successfully initialized Closet Service', 'success')