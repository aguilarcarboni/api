from sqlalchemy import Boolean, create_engine, Column, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from src.utils.managers.database_manager import DatabaseManager
from src.utils.logger import logger
import uuid
from datetime import datetime

import os

class SQLite:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLite, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.announcement('Initializing SQLite Service', 'info')

            self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'laserfocus.db')
            
            self.db_url = 'sqlite:///laserfocus.db'
            self.engine = create_engine(self.db_url)
            
            self.Base = declarative_base()
            self._setup_models()
            
            self.db = DatabaseManager(base=self.Base, engine=self.engine)
            
            logger.announcement('Successfully initialized SQLite Service', 'success')
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

        # Store model classes as attributes of the instance
        self.User = User

# Create a single instance that can be imported and used throughout the application
db = SQLite().db