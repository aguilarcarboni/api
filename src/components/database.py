import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from functools import wraps
from typing import Dict, Any

from src.utils.response import Response
from src.utils.logger import logger

logger.announcement('Initializing Laserfocus Database', 'info')

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

logger.announcement('Successfully initialized Laserfocus Database', 'success')

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
def create(session, table: str, data: dict):
    logger.info(f'Attempting to create new entry in table: {table}')

    try:
        tbl = Table(table, metadata, autoload_with=engine)
        current_time = datetime.now()
        data = {
            'created': current_time,
            'updated': current_time,
            **data
        }
        new_record = tbl.insert().values(**data)
        result = session.execute(new_record)
        session.flush()
        new_id = result.inserted_primary_key[0]

        # Replace this
        logger.success(f'Successfully created entry with id: {new_id}')
        return Response.success(new_id)
    
    except Exception as e:
        logger.error(f'Error creating record: {str(e)}')
        return Response.error(f'Database error: {str(e)}')

@with_session
def update(session, table: str, params: dict, data: dict):
    logger.info(f'Attempting to update entry in table: {table} with params: {params}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        for key, value in params.items():
            if hasattr(tbl.c, key):
                query = query.filter(getattr(tbl.c, key) == value)

        item = query.first()

        if not item:
            return Response.error(f"{table.capitalize()} with given parameters not found")
        
        logger.info(f'Updating entry timestamp.')
        data['updated'] = datetime.now()

        query.update(data)
        session.flush()

        updated_item = query.first()
        logger.success(f"Successfully updated entry with id: {updated_item.id} in table: {table}.")

        return Response.success(updated_item.id)
    
    except Exception as e:
        logger.error(f"Error updating {table}: {str(e)}")
        return Response.error(f"Database error: {str(e)}")

@with_session
def read(session, table: str, params: dict = None):
    logger.info(f'Attempting to read entry from table: {table} with params: {params}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        if params:
            for key, value in params.items():
                if hasattr(tbl.c, key):
                    query = query.filter(getattr(tbl.c, key) == value)
            
        results = query.all()

        serialized_results = [row._asdict() for row in results]
        
        logger.success(f'Successfully read {len(serialized_results)} entries from table: {table}')
        return Response.success(serialized_results)
    
    except Exception as e:
        logger.error(f'Error reading from database: {str(e)}')
        return Response.error(f"Database error: {str(e)}")

@with_session
def delete(session, table: str, params: dict):
    logger.info(f'Attempting to delete entry from table: {table} with params: {params}')
    
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)

        for key, value in params.items():
            if hasattr(tbl.c, key):
                query = query.filter(getattr(tbl.c, key) == value)

        item = query.first()
        if not item:
            return Response.error(f"Entry with given parameters not found in table: {table}.")

        delete_stmt = tbl.delete().where(tbl.c.id == item.id)
        session.execute(delete_stmt)
        session.flush()

        logger.success(f"Successfully deleted entry with id: {item.id} from table: {table}.")
        return Response.success(item.id)
    
    except Exception as e:
        logger.error(f"Error deleting {table}: {str(e)}")
        return Response.error(f"Database error: {str(e)}")

@with_session
def get_parent_lineage(session, table: str, params: dict, depth: int) -> Response:
    """
    Wrapper function to get the parent lineage of a table up to a specified depth.

    Args:
        session: The database session.
        table (str): The name of the table to start the lineage from.
        params (dict): Parameters to identify the specific record.
        depth (int): The maximum depth of recursion (default is 3).

    Returns:
        Response: A Response object containing the parent lineage or an error message.
    """
    try:
        logger.info(f"Attempting to retrieve parent lineage for table: {table} with depth: {depth}.")
        lineage = get_parent_lineage_recursive(session,table, params, depth, 1)
        if not lineage:
            return Response.error("Failed to retrieve parent lineage")
        return Response.success(lineage) 
    
    except Exception as e:
        logger.error(f"Error in get_parent_lineage: {str(e)}")
        return Response.error(f"Failed to retrieve parent lineage: {str(e)}")
    
def get_foreign_keys(session, table: str, params: dict) -> Dict[str, str]:
    """
    Helper function to get foreign keys for a table.

    Args:
        table (str): The name of the table to get foreign keys for.

    Returns:
        Dict[str, str]: A dictionary where keys are column names and values are the referenced tables.
    """
    try:
        tbl = Table(table, metadata, autoload_with=engine)
        foreign_keys = {}
        for column in tbl.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    foreign_keys[column.name] = fk.column.table.name
        
        # Query data using table and params to find the space_id
        keys = {}
        tbl = Table(table, metadata, autoload_with=engine)
        query = session.query(tbl)
        for key, value in params.items():
            if hasattr(tbl.c, key):
                query = query.filter(getattr(tbl.c, key) == value)
        item = query.first()
        if item:
            for column_name, _ in foreign_keys.items():
                if hasattr(item, column_name):
                    keys[column_name] = getattr(item, column_name)

        logger.success(f"Successfully retrieved foreign keys for table: {table}, result: {keys}")
        return Response.success(keys)
    except Exception as e:
        logger.error(f"Error retrieving foreign keys for table {table}: {str(e)}")
        return Response.error(f"Failed to retrieve foreign keys: {str(e)}")

def get_parent_lineage_recursive(session, table: str, params: dict, depth: int, current_depth: int) -> Dict[str, Any]:
    """
    Recursive helper function to get the parent lineage of a table up to a specified depth.
    Returns a dictionary structure suitable for graphing in a directed graph.
    """
    if current_depth > depth:
        return {}

    try:
        foreign_keys_response = get_foreign_keys(session, table, params)
        if foreign_keys_response['status'] != 'success':
            return {}

        foreign_keys = foreign_keys_response['content']
        node = {
            'id': f"{table}_{params.get('id', '')}",
            'label': table,
            'depth': current_depth,
            'children': []
        }

        for column_name, foreign_key_value in foreign_keys.items():
            foreign_key = next(iter(Table(table, metadata, autoload_with=engine).columns[column_name].foreign_keys))
            referenced_table = foreign_key.column.table.name
            child_node = get_parent_lineage_recursive(session, referenced_table, {'id': foreign_key_value}, depth - 1, current_depth + 1)
            if child_node:
                node['children'].append(child_node)

        return node
    except Exception as e:
        logger.error(f"Error retrieving parent lineage for table {table}: {str(e)}")
        return Response.error(f"Failed to retrieve parent lineage: {str(e)}")
