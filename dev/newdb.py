import os
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, errors
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import certifi
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        logger.info("Initializing database client.")
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        self.client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
        logger.info("Successfully initialized database client.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def query_document(self, database: str, collection: str, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Query a single document from the specified database and collection.

        Args:
            database (str): The name of the database.
            collection (str): The name of the collection.
            query (Dict[str, Any]): The query to filter documents.
            projection (Optional[Dict[str, Any]]): The projection to apply to the result.

        Returns:
            Optional[Dict[str, Any]]: The matching document, or None if not found.
        """
        try:
            with self.client.start_session() as session:
                db = self.client[database]
                coll = db[collection]
                return coll.find_one(query, projection, session=session)
        except errors.PyMongoError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def query_documents(self, database: str, collection: str, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query multiple documents from the specified database and collection.

        Args:
            database (str): The name of the database.
            collection (str): The name of the collection.
            query (Dict[str, Any]): The query to filter documents.
            projection (Optional[Dict[str, Any]]): The projection to apply to the results.

        Returns:
            List[Dict[str, Any]]: A list of matching documents.
        """
        try:
            with self.client.start_session() as session:
                db = self.client[database]
                coll = db[collection]
                return list(coll.find(query, projection, session=session))
        except errors.PyMongoError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def insert_document(self, database: str, collection: str, document: Dict[str, Any]) -> str:
        """
        Insert a document into the specified database and collection.

        Args:
            database (str): The name of the database.
            collection (str): The name of the collection.
            document (Dict[str, Any]): The document to insert.

        Returns:
            str: The inserted document's ID.
        """
        try:
            with self.client.start_session() as session:
                db = self.client[database]
                coll = db[collection]
                result = coll.insert_one(document, session=session)
                return str(result.inserted_id)
        except errors.PyMongoError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def update_document(self, database: str, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update a document in the specified database and collection.

        Args:
            database (str): The name of the database.
            collection (str): The name of the collection.
            query (Dict[str, Any]): The query to find the document to update.
            update (Dict[str, Any]): The update to apply to the document.

        Returns:
            int: The number of documents modified.
        """
        try:
            with self.client.start_session() as session:
                db = self.client[database]
                coll = db[collection]
                result = coll.update_one(query, update, session=session)
                return result.modified_count
        except errors.PyMongoError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def delete_document(self, database: str, collection: str, query: Dict[str, Any]) -> int:
        """
        Delete a document from the specified database and collection.

        Args:
            database (str): The name of the database.
            collection (str): The name of the collection.
            query (Dict[str, Any]): The query to find the document to delete.

        Returns:
            int: The number of documents deleted.
        """
        try:
            with self.client.start_session() as session:
                db = self.client[database]
                coll = db[collection]
                result = coll.delete_one(query, session=session)
                return result.deleted_count
        except errors.PyMongoError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise

    def convert_id_to_object_id(self, id_str: str) -> ObjectId:
        """
        Convert a string ID to a MongoDB ObjectId.

        Args:
            id_str (str): The string representation of the ID.

        Returns:
            ObjectId: The converted ObjectId.
        """
        try:
            return ObjectId(id_str)
        except Exception as e:
            logger.error(f"Error converting to ObjectId: {str(e)}")
            raise ValueError(f"Invalid ObjectId string: {id_str}")