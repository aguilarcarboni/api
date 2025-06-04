from sqlalchemy import Boolean, create_engine, Column, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from laserfocus.utils.managers.database import DatabaseManager
from laserfocus.utils.logger import logger
import uuid
from datetime import datetime

import os

class Supabase:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Supabase, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.announcement('Initializing Database Service', 'info')
            
            self.db_url = 'sqlite:///laserfocus.db'
            self.engine = create_engine(self.db_url)
            
            self.Base = declarative_base()
            self._setup_models()
            
            self.db = DatabaseManager(base=self.Base, engine=self.engine)
            
            logger.announcement('Successfully initialized Database Service', 'success')
            self._initialized = True

    def _setup_models(self):

        class User(self.Base):
            __tablename__ = 'user'
            id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            created = Column(Text, nullable=False, default=datetime.now().strftime('%Y%m%d%H%M%S'))
            updated = Column(Text, nullable=False, default=datetime.now().strftime('%Y%m%d%H%M%S'))
            email = Column(Text, nullable=False, unique=True)
            image = Column(Text, nullable=True)
            password = Column(Text, nullable=False)
            scopes = Column(Text, nullable=False)
            name = Column(Text, nullable=False)

        class Event(self.Base):
            __tablename__ = 'event'
            id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            name = Column(Text, nullable=False)
            updated = Column(Text, nullable=False, default=datetime.now().strftime('%Y%m%d%H%M%S'))
            created = Column(Text, nullable=False, default=datetime.now().strftime('%Y%m%d%H%M%S'))
            status = Column(Text, nullable=False)
            visibility = Column(Text, nullable=False)
            description = Column(Text, nullable=False)
            start = Column(Text, nullable=False)
            all_day = Column(Boolean, nullable=False)
            ends = Column(Text, nullable=False)
            is_recurring = Column(Boolean, nullable=False)
            recurring_interval = Column(Integer, nullable=False)
            recurring_end = Column(Text, nullable=False)
            transparency = Column(Text, nullable=False)
            location = Column(JSON, nullable=False)

        # Store model classes as attributes of the instance
        self.User = User
        self.Event = Event

# Create a single instance that can be imported and used throughout the application
db = Supabase().db