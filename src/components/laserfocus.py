from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.utils.database import DatabaseHandler
import os

from src.utils.logger import logger

logger.announcement('Initializing Database Service', 'info')

db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'laserfocus.db')
db_url = f'sqlite:///{db_path}'
engine = create_engine(db_url)

Base = declarative_base()

class Space(Base):
    """Space table"""
    __tablename__ = 'space'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    updated = Column(String)
    created = Column(String)
    status = Column(String)
    visibility = Column(String)

class Task(Base):
    """Task table"""
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, unique=True)
    space_id = Column(Integer, ForeignKey('space.id'))
    name = Column(String)
    updated = Column(String)
    created = Column(String)
    status = Column(String)
    visibility = Column(String)
    due = Column(String)
    priority = Column(String)

class TaskLink(Base):
    """TaskLink table"""
    __tablename__ = 'task_link'
    id = Column(Integer, primary_key=True, unique=True)
    from_task_id = Column(Integer)
    to_task_id = Column(Integer)
    updated = Column(String)
    created = Column(String)

class Event(Base):
    """Event table"""
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, unique=True)
    space_id = Column(Integer, ForeignKey('space.id'))
    name = Column(String)
    updated = Column(String)
    created = Column(String)
    status = Column(String)
    visibility = Column(String)
    description = Column(String)
    start = Column(String)
    all_day = Column(Boolean)
    ends = Column(String)
    is_recurring = Column(Boolean)
    recurring_interval = Column(Integer)
    recurring_end = Column(String)
    transparency = Column(String)
    location = Column(JSON)

class Journal(Base):
    """Journal table"""
    __tablename__ = 'journal'
    id = Column(Integer, primary_key=True, unique=True)
    space_id = Column(Integer, ForeignKey('space.id'))
    name = Column(String)
    updated = Column(String)
    created = Column(String)
    status = Column(String)
    visibility = Column(String)
    description = Column(String)

class Page(Base):
    """Page table"""
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True, unique=True)
    journal_id = Column(Integer, ForeignKey('journal.id'))
    name = Column(String)
    updated = Column(String)
    created = Column(String)
    status = Column(String)
    visibility = Column(String)
    content = Column(String)

class PageLink(Base):
    """PageLink table"""
    __tablename__ = 'page_link'
    id = Column(Integer, primary_key=True, unique=True)
    from_page_id = Column(Integer, ForeignKey('page.id'))
    to_page_id = Column(Integer, ForeignKey('page.id'))
    updated = Column(String)
    created = Column(String)    

db = DatabaseHandler(base=Base, engine=engine, type='sqlite')

#db.create('space', {'name': 'Default', 'status': 'active', 'visibility': 'private'})

logger.announcement("Successfully initialized Database Service", type='success')