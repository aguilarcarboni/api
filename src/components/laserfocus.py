from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
import os

from laserfocus.utils.database import DatabaseHandler
from laserfocus.utils.logger import logger

class LaserFocus:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LaserFocus, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.announcement('Initializing Database Service', 'info')

            db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'laserfocus.db')
            db_url = f'sqlite:///{db_path}'
            self.engine = create_engine(db_url)

            self.Base = declarative_base()
            self._setup_models()
            self.db = DatabaseHandler(base=self.Base, engine=self.engine, type='sqlite')

            # Create fake data for user
            self.db.create(table='user', data={'name': 'Andres', 'status': 'active', 'visibility': 'private', 'role': 'owner', 'email': 'aguilarcarboni@gmail.com', 'password': 'Jxk5odrUasO9k7Su', 'username': 'aguilarcarboni', 'space_id': 1, 'image': None})
            self.db.create(table='space', data={'name': 'Default', 'status': 'active', 'visibility': 'public'})

            # Create fake data for project
            self.db.create(table='project', data={'name': 'Home', 'status': 'active', 'visibility': 'public', 'space_id': 2})
            self.db.create(table='space', data={'name': 'Home', 'status': 'active', 'visibility': 'public'})
            self.db.create(table='task', data={'name': 'Default', 'status': 'active', 'visibility': 'public', 'space_id': 2, 'due': '2025-01-01', 'priority': 1})
            
            logger.announcement("Successfully initialized Database Service", type='success')
            self._initialized = True

    def _setup_models(self):

        class User(self.Base):
            """User table"""
            __tablename__ = 'user'
            id = Column(Integer, primary_key=True, unique=True)
            name = Column(String, nullable=False)
            status = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            visibility = Column(String, nullable=False)
            role = Column(String, nullable=False)
            email = Column(String, unique=True, nullable=False)
            password = Column(String, nullable=False)
            username = Column(String, unique=True, nullable=False)
            space_id = Column(Integer, unique=True, nullable=False)
            image = Column(String, nullable=True)

        class Space(self.Base):
            """Space table"""
            __tablename__ = 'space'
            id = Column(Integer, primary_key=True, unique=True)
            name = Column(String, unique=True, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)

        class Project(self.Base):
            """Project table"""
            __tablename__ = 'project'
            id = Column(Integer, primary_key=True, unique=True)
            space_id = Column(Integer, ForeignKey('space.id'), nullable=False)
            name = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)

        class Task(self.Base):
            """Task table"""
            __tablename__ = 'task'
            id = Column(Integer, primary_key=True, unique=True)
            space_id = Column(Integer, ForeignKey('space.id'), nullable=False)
            name = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)
            due = Column(String, nullable=False)
            priority = Column(Integer, nullable=False)

        class TaskLink(self.Base):
            """TaskLink table"""
            __tablename__ = 'task_link'
            id = Column(Integer, primary_key=True, unique=True)
            from_task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
            to_task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)

        class Event(self.Base):
            """Event table"""
            __tablename__ = 'event'
            id = Column(Integer, primary_key=True, unique=True)
            space_id = Column(Integer, ForeignKey('space.id'))
            name = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)
            description = Column(String, nullable=False)
            start = Column(String, nullable=False)
            all_day = Column(Boolean, nullable=False)
            ends = Column(String, nullable=False)
            is_recurring = Column(Boolean, nullable=False)
            recurring_interval = Column(Integer, nullable=False)
            recurring_end = Column(String, nullable=False)
            transparency = Column(String, nullable=False)
            location = Column(JSON, nullable=False)

        class Journal(self.Base):
            """Journal table"""
            __tablename__ = 'journal'
            id = Column(Integer, primary_key=True, unique=True)
            space_id = Column(Integer, ForeignKey('space.id'), nullable=False)
            name = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)
            description = Column(String, nullable=False)

        class Page(self.Base):
            """Page table"""
            __tablename__ = 'page'
            id = Column(Integer, primary_key=True, unique=True)
            journal_id = Column(Integer, ForeignKey('journal.id'), nullable=False)
            name = Column(String, nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
            status = Column(String, nullable=False)
            visibility = Column(String, nullable=False)
            content = Column(String, nullable=False)

        class PageLink(self.Base):
            """PageLink table"""
            __tablename__ = 'page_link'
            id = Column(Integer, primary_key=True, unique=True)
            from_page_id = Column(Integer, ForeignKey('page.id'), nullable=False)
            to_page_id = Column(Integer, ForeignKey('page.id'), nullable=False)
            updated = Column(String, nullable=False)
            created = Column(String, nullable=False)
        

        # Store model classes as attributes of the instance
        self.User = User
        self.Space = Space
        self.Project = Project
        self.Task = Task
        self.TaskLink = TaskLink
        self.Event = Event
        self.Journal = Journal
        self.Page = Page
        self.PageLink = PageLink

# Create a single instance that can be imported and used throughout the application
laserfocus = LaserFocus()