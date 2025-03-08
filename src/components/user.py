from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
import os

from laserfocus.utils.database import DatabaseHandler
from laserfocus.utils.logger import logger

logger.announcement('Initializing User Service', 'info')

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'users.db')
db_url = f'sqlite:///{db_path}'
engine = create_engine(db_url)

Base = declarative_base()

class User(Base):
    """User table"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    status = Column(String)
    updated = Column(String)
    created = Column(String)
    visibility = Column(String)
    role = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    username = Column(String, unique=True)
    space_id = Column(Integer, unique=True)
    image = Column(String, nullable=True)

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')
db.create('user', {'name': 'Andres', 'status': 'active', 'visibility': 'private', 'role': 'owner', 'email': 'aguilarcarboni@gmail.com', 'password': 'Jxk5odrUasO9k7Su', 'username': 'aguilarcarboni', 'space_id': 1, 'image': None})
logger.announcement("Successfully initialized User Service", type='success')