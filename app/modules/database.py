import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, Column, Integer, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.helpers.response import Response
from app.helpers.logger import logger

from datetime import datetime
from typing import Optional

# SQLAlchemy setup
load_dotenv()
DATABASE_URL = os.getenv("SUPABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the .env file")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
logger.info('Successfully connected to database')

# Define models
class user(Base):

    __tablename__ = "user"
    space = relationship("space", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Base fields
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

    # User specific fields
    role = Column(Text, nullable=False)

class space(Base):

    __tablename__ = "space"
    user = relationship("user", back_populates="space", uselist=False)
    events = relationship("event", back_populates="space", cascade="all, delete-orphan")

    # Relationship fields
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)

    # Base fields
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

class event(Base):

    __tablename__ = "event"

        # Relationship fields
    space = relationship("space", back_populates="event", uselist=False)
    space_id = Column(Integer, ForeignKey("space.id"), nullable=False)

    #contacts = relationship("contact", back_populates="event")
    #contact_id = Column(Integer, ForeignKey("contact.id"), nullable=True)

    # Base fields
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

    # Event specific fields
    description = Column(Text)

    start = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, nullable=False)
    ends = Column(DateTime(timezone=True))

    is_recurring = Column(Boolean, nullable=False)
    recurring_interval = Column(Integer)
    recurring_end = Column(DateTime(timezone=True))
    
    transparency = Column(Text, nullable=False)
    location = Column(JSON)

class contact(Base):

    __tablename__ = "contact"

    event = relationship("event", back_populates="contacts")

    # Base fields
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

    # Contact specific fields
    email = Column(Text)
    phone = Column(Text)


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
        self.start = start
        self.all_day = all_day
        self.ends = ends
        self.is_recurring = is_recurring
        self.recurring_interval = recurring_interval
        self.recurring_end = recurring_end
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
            end=event_orm.end,
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
            end=self.end,
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


# Create tables
Base.metadata.create_all(bind=engine)

"""Database functions"""
def get_db_session():
    """Create and yield a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create(data: user | space | event):

    db = next(get_db_session())
    try:
        
        db.add(data)
        db.commit()
        db.refresh(data)

        return Response.success(f'Successfully created {data.id}')
    
    except SQLAlchemyError as e:
        db.rollback()
        return Response.error(f"Error creating {str(e)}")

def read(table: str, params: dict):
    db = next(get_db_session())
    try:
        # Get the model class dynamically
        model = globals()[table]
        
        # Create a query
        query = db.query(model)
        
        # Apply filters based on params
        for key, value in params.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        
        # Execute the query
        results = query.all()
        
        # Convert results to dict
        serialized_results = []
        for result in results:
            item_dict = {}
            for column in inspect(model).columns:
                item_dict[column.name] = getattr(result, column.name)
            serialized_results.append(item_dict)
        
        return Response.success(serialized_results)
    
    except (KeyError, AttributeError):
        return Response.error(f"Invalid table name or parameter: {table}")
    except SQLAlchemyError as e:
        return Response.error(f"Error reading from database: {str(e)}")

def delete(table: str, params: dict):
    db = next(get_db_session())
    try:
        # Get the model class dynamically
        model = globals()[table]
        
        # Create a query
        query = db.query(model)
        
        # Apply filters based on params
        for key, value in params.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        
        # Query the item
        item = query.first()
        if not item:
            return Response.error(f"{table.capitalize()} with given parameters not found")
        
        # Delete the item
        db.delete(item)
        db.commit()
        
        return Response.success(f"{table.capitalize()} deleted successfully")
    except KeyError:
        return Response.error(f"Invalid table name: {table}")
    except SQLAlchemyError as e:
        db.rollback()
        return Response.error(f"Error deleting {table}: {str(e)}")
