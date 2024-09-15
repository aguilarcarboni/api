import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, ForeignKey, DateTime, Text, Boolean, inspect
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

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(Text)
    description = Column(Text)
    role = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

class space(Base):

    __tablename__ = "space"
    user = relationship("user", back_populates="space", uselist=False)
    events = relationship("event", back_populates="space", cascade="all, delete-orphan")

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    name = Column(Text, index=True)
    description = Column(Text)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)

class event(Base):

    __tablename__ = "event"
    space = relationship("space", back_populates="events", uselist=False)

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("space.id"))
    name = Column(Text, index=True, nullable=False)
    description = Column(Text)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean)
    updated = Column(DateTime(timezone=True), nullable=False)
    created = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    visibility = Column(Text, nullable=False)
    transparency = Column(Text, nullable=False)



class UserPayload:
    
    def __init__(
        self,
        name: str,
        role: str,
        status: str,
        visibility: str,
        description: Optional[str] = None,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.name = name
        self.description = description
        self.role = role
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility

    @classmethod
    def from_orm(cls, user_orm: user):
        return cls(
            name=user_orm.name,
            description=user_orm.description,
            role=user_orm.role,
            updated=user_orm.updated,
            created=user_orm.created,
            status=user_orm.status,
            visibility=user_orm.visibility
        )

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "role": self.role,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility
        }

    def to_orm(self) -> user:
        return user(
            name=self.name,
            description=self.description,
            role=self.role,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility
        )

class SpacePayload:

    def __init__(
        self,
        name: str,
        status: str,
        user_id: int,
        description: Optional[str] = None,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
        visibility: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created
        self.status = status
        self.visibility = visibility
        self.user_id = user_id

    @classmethod
    def from_orm(cls, space_orm: space):
        return cls(
            name=space_orm.name,
            user_id=space_orm.user_id,
            description=space_orm.description,
            updated=space_orm.updated,
            created=space_orm.created,
            status=space_orm.status,
            visibility=space_orm.visibility
        )

    def to_dict(self):
        return {
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None,
            "status": self.status,
            "visibility": self.visibility
        }

    def to_orm(self) -> space:
        return space(
            name=self.name,
            user_id=self.user_id,
            description=self.description,
            updated=self.updated,
            created=self.created,
            status=self.status,
            visibility=self.visibility
        )

class EventPayload:

    def __init__(
        self,
        name: str,
        space_id: int,
        description: str,
        start: datetime,
        end: datetime,
        status: str,
        visibility: str,
        transparency: str,
        all_day: Optional[bool] = None,
        updated: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.name = name
        self.space_id = space_id
        self.description = description
        self.start = start
        self.end = end
        self.status = status
        self.visibility = visibility
        self.transparency = transparency
        self.all_day = all_day
        self.updated = datetime.now() if updated is None else updated
        self.created = datetime.now() if created is None else created

    @classmethod
    def from_orm(cls, event_orm: event):
        return cls(
            name=event_orm.name,
            space_id=event_orm.space_id,
            description=event_orm.description,
            start=event_orm.start,
            end=event_orm.end,
            status=event_orm.status,
            visibility=event_orm.visibility,
            transparency=event_orm.transparency,
            all_day=event_orm.all_day,
            updated=event_orm.updated,
            created=event_orm.created
        )

    def to_dict(self):
        return {
            "name": self.name,
            "space_id": self.space_id,
            "description": self.description,
            "start": self.start.isoformat() if self.start else None,
            "end": self.end.isoformat() if self.end else None,
            "status": self.status,
            "visibility": self.visibility,
            "transparency": self.transparency,
            "all_day": self.all_day,
            "updated": self.updated.isoformat() if self.updated else None,
            "created": self.created.isoformat() if self.created else None
        }

    def to_orm(self) -> event:
        return event(
            name=self.name,
            space_id=self.space_id,
            description=self.description,
            start=self.start,
            end=self.end,
            status=self.status,
            visibility=self.visibility,
            transparency=self.transparency,
            all_day=self.all_day,
            updated=self.updated,
            created=self.created
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
