import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from src.utils.database import DatabaseHandler
from src.utils.logger import logger

logger.announcement('Initializing Laserfocus Database', 'info')

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the .env file")

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_recycle=3600)

# Use reflection to load the existing tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Create a base class for reflected tables
Base = automap_base(metadata=metadata)
Base.prepare()

db = DatabaseHandler(base=Base, engine=engine, type='Supabase')

logger.announcement('Successfully initialized Laserfocus Database', 'success')