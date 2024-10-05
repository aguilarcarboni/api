import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, inspect, Table
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from functools import wraps
from typing import Optional

from app.helpers.response import Response
from app.helpers.logger import logger

logger.info('Initializing Database')

# SQLAlchemy setup with connection pooling
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the .env file")

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_recycle=3600)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Use reflection to load the existing tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Create a base class for reflected tables
Base = automap_base(metadata=metadata)
Base.prepare()

# Get the reflected table classes
user = Base.classes.user
space = Base.classes.space
event = Base.classes.event
contact = Base.classes.contact
page = Base.classes.page

logger.success('Successfully initialized Database')

# Define Payload classes
class UserPayload:
    
    def __init__(
        self,
        name: str,
        status: str,
        visibility: str,
        role: str,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.name = name
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility
        self.role = role

    @classmethod
    def from_orm(cls, user_orm: user):
        return cls(
            name=user_orm.name,
            updated=user_orm.updated,
            created=user_orm.created,
            status=user_orm.status,
            visibility=user_orm.visibility,
            role=user_orm.role
        )

    def to_dict(self):
        return {
            "name": self.name,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility,
            "role": self.role
        }

    def to_orm(self) -> user:
        return user(
            name=self.name,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility,
            role=self.role
        )

class SpacePayload:

    def __init__(
        self,
        user_id: int,
        name: str,
        status: str,
        visibility: str,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.name = name
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility

    @classmethod
    def from_orm(cls, space_orm: space):
        return cls(
            user_id=space_orm.user_id,
            name=space_orm.name,
            updated=space_orm.updated,
            created=space_orm.created,
            status=space_orm.status,
            visibility=space_orm.visibility
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility
        }

    def to_orm(self) -> space:
        return space(
            user_id=self.user_id,
            name=self.name,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility
        )

class EventPayload:

    def __init__(
        self,
        space_id: int,
        name: str,
        status: str,
        visibility: str,
        start: datetime,
        all_day: bool,
        is_recurring: bool,
        transparency: str,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
        description: Optional[str] = None,
        ends: Optional[datetime] = None,
        recurring_interval: Optional[int] = None,
        recurring_end: Optional[datetime] = None,
        location: Optional[dict] = None,
    ):
        self.space_id = space_id

        self.name = name
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility

        self.description = description

        try:
            if isinstance(start, str):
                self.start = datetime.fromisoformat(start)
            else:
                self.start = start
        except ValueError as e:
            logger.error(f"Error parsing start date: {str(e)}")
            raise ValueError(f"Invalid start date format: {start}")

        try:
            if isinstance(ends, str):
                self.ends = datetime.fromisoformat(ends)
            else:
                self.ends = ends
        except ValueError as e:
            logger.error(f"Error parsing ends date: {str(e)}")
            raise ValueError(f"Invalid ends date format: {ends}")

        try:
            if isinstance(recurring_end, str):
                self.recurring_end = datetime.fromisoformat(recurring_end)
            else:
                self.recurring_end = recurring_end
        except ValueError as e:
            logger.error(f"Error parsing recurring_end date: {str(e)}")
            raise ValueError(f"Invalid recurring_end date format: {recurring_end}")

        self.all_day = all_day
        self.is_recurring = is_recurring
        self.recurring_interval = recurring_interval
        self.transparency = transparency
        self.location = location

    @classmethod
    def from_orm(cls, event_orm: event):
        return cls(
            space_id=event_orm.space_id,
            name=event_orm.name,
            updated=event_orm.updated,
            created=event_orm.created,
            status=event_orm.status,
            visibility=event_orm.visibility,
            description=event_orm.description,
            start=event_orm.start,
            all_day=event_orm.all_day,
            ends=event_orm.ends,
            is_recurring=event_orm.is_recurring,
            recurring_interval=event_orm.recurring_interval,
            recurring_end=event_orm.recurring_end,
            transparency=event_orm.transparency,
            location=event_orm.location
        )

    def to_dict(self):
        return {
            "space_id": self.space_id,
            "name": self.name,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility,
            "description": self.description,
            "start": self.start.isoformat(),
            "all_day": self.all_day,
            "ends": self.ends.isoformat() if self.ends else None,
            "is_recurring": self.is_recurring,
            "recurring_interval": self.recurring_interval,
            "recurring_end": self.recurring_end.isoformat() if self.recurring_end else None,
            "transparency": self.transparency,
            "location": self.location
        }

    def to_orm(self) -> event:
        return event(
            space_id=self.space_id,
            name=self.name,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility,
            description=self.description,
            start=self.start,
            all_day=self.all_day,
            ends=self.ends,
            is_recurring=self.is_recurring,
            recurring_interval=self.recurring_interval,
            recurring_end=self.recurring_end,
            transparency=self.transparency,
            location=self.location
        )

class ContactPayload:

    def __init__(
        self,
        name: str,
        status: str,
        visibility: str,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
        email: Optional[str] = None,    
        phone: Optional[str] = None,
    ):
        self.name = name
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility
        self.email = email
        self.phone = phone
    
    @classmethod
    def from_orm(cls, contact_orm: contact):
        return cls(
            name=contact_orm.name,
            updated=contact_orm.updated,
            created=contact_orm.created,
            status=contact_orm.status,
            visibility=contact_orm.visibility,
            email=contact_orm.email,
            phone=contact_orm.phone
        )

    def to_dict(self):
        return {
            "name": self.name,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility,
            "email": self.email,
            "phone": self.phone
        }

    def to_orm(self) -> contact:
        return contact(
            name=self.name,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility,
            email=self.email,
            phone=self.phone
        )

class PagePayload:

    def __init__(
        self,
        journal_id: int,
        name: str,
        status: str,
        visibility: str,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.journal_id = journal_id
        self.name = name
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility

    @classmethod
    def from_orm(cls, page_orm: page):
        return cls(
            journal_id=page_orm.journal_id,
            name=page_orm.name,
            updated=page_orm.updated,
            created=page_orm.created,
            status=page_orm.status,
            visibility=page_orm.visibility
        )
    
    def to_dict(self):
        return {
            "journal_id": self.journal_id,
            "name": self.name,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility
        }
    
    def to_orm(self) -> page:
        return page(
            journal_id=self.journal_id,
            name=self.name,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility
        )
    

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            return Response.error(f"Database error: {str(e)}")
        finally:
            session.close()
    return wrapper

@with_session
def create(session, table_name: str, data: dict):
    logger.info(f'Attempting to create new entry in table: {table_name}')

    try:
        if table_name == 'user':
            payload = UserPayload(**data)
            new_record = user(**payload.to_dict())
        elif table_name == 'space':
            payload = SpacePayload(**data)
            new_record = space(**payload.to_dict())
        elif table_name == 'event':
            payload = EventPayload(**data)
            new_record = event(**payload.to_dict())
        elif table_name == 'page':
            payload = PagePayload(**data)
            new_record = page(**payload.to_dict())
        else:
            raise ValueError(f"Invalid table {table_name}")

        session.add(new_record)
        session.flush()
        logger.success(f'Successfully created entry: {new_record.id}')
        return Response.success(f'{new_record.id}')
    except SQLAlchemyError as e:
        logger.error(f'Error creating {str(e)}')
        raise

@with_session
def update(session, table_name: str, params: dict, data: dict):
    logger.info(f'Attempting to update entry in table: {table_name}')
    
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        query = session.query(table)

        for key, value in params.items():
            if hasattr(table.c, key):
                query = query.filter(getattr(table.c, key) == value)

        item = query.first()

        if not item:
            return Response.error(f"{table_name.capitalize()} with given parameters not found")

        query.update(data)
        session.flush()

        updated_item = query.first()
        logger.success(f"Successfully updated {table_name} with new data {updated_item._asdict()}")
        return Response.success(f"Successfully updated {table_name} with new data {updated_item._asdict()}")
    except SQLAlchemyError as e:
        logger.error(f"Error updating {table_name}: {str(e)}")
        raise

@with_session
def read(session, table: str, params: dict = None):
    logger.info(f'Attempting to read entry from table: {table}')
    
    try:
        table = Table(table, metadata, autoload_with=engine)
        query = session.query(table)

        if params:
            for key, value in params.items():
                if hasattr(table.c, key):
                    query = query.filter(getattr(table.c, key) == value)
            
        results = query.all()

        serialized_results = [row._asdict() for row in results]
        
        logger.success(f'Successfully read {len(serialized_results)} entries from table: {table}')
        return Response.success(serialized_results)
    except SQLAlchemyError as e:
        logger.error(f'Error reading from database: {str(e)}')
        raise

@with_session
def delete(session, table: str, params: dict):
    logger.info(f'Attempting to delete entry from table: {table}')
    
    try:
        table_map = {
            'user': user,
            'space': space,
            'event': event,
            'contact': contact,
            'page': page
        }
        
        if table not in table_map:
            return Response.error(f"Invalid table name: {table}")
        
        Model = table_map[table]
        query = session.query(Model)
        
        for key, value in params.items():
            if hasattr(Model, key):
                query = query.filter(getattr(Model, key) == value)
        
        item = query.first()
        if not item:
            return Response.error(f"{table.capitalize()} with given parameters not found")
        
        session.delete(item)
        session.flush()

        logger.success(f"Successfully deleted {table} with id: {item.id}")
        return Response.success(f"{table.capitalize()} deleted successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error deleting {table}: {str(e)}")
        raise