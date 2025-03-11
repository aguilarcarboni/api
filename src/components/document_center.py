from src.components.drive import GoogleDrive
from src.lib.entities.document import Document
from laserfocus.utils.exception import handle_exception
import json
from datetime import datetime

drive = GoogleDrive()

from laserfocus.utils.database import DatabaseHandler
from laserfocus.utils.logger import logger
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
import os

class DocumentCenter:
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Get or create the singleton instance of DocumentCenter.
        
        Returns:
            DocumentCenter: The singleton instance of DocumentCenter
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DocumentCenter._instance is not None:
            logger.announcement('Using existing Document Center Service', 'info')
            return
        
        logger.announcement('Initializing Document Center Service', 'info')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'document_center.db')
        db_url = f'sqlite:///{db_path}'

        self.default_folder_dictionary = [
            {
                'drive_id': '1jwcL1lpB9gvkH886pSTQytbKhrsslyP8',
                'id': 'document',
                'label': 'Document'
            },
            {
                'drive_id': '12313123123123123',
                'id': 'other',
                'label': 'Other'
            }
        ]
        
        self.engine = create_engine(db_url)

        self.Base = declarative_base()
        self._setup_models()
        self.db = DatabaseHandler(base=self.Base, engine=self.engine, type='sqlite')

        logger.announcement("Successfully initialized Document Center Service", type='success')

    def _setup_models(self):

        class Document(self.Base):
            """Document table"""
            __tablename__ = 'document'
            id = Column(Integer, primary_key=True, unique=True)
            document_id = Column(String, nullable=False)
            document_info = Column(JSON, nullable=False)
            file_info = Column(JSON, nullable=False)
            uploader = Column(String, nullable=False)
            created = Column(String, nullable=False)
            updated = Column(String, nullable=False)
        
        self.Document = Document

    @handle_exception
    def get_folder_dictionary(self):
        return self.default_folder_dictionary

    @handle_exception
    def read_files(self, params):
        files = {}

        # TODO Fix this so that I can use multiple drive ids
        for folder in self.default_folder_dictionary:
            files_in_folder = self.db.read(table='document', params=params)
            files[folder['id']] = json.loads(files_in_folder.data.decode("utf-8"))

        if len(files) == 0:
            raise Exception("No files found")
        
        return files
    
    @handle_exception
    def delete_file(self, document: Document):
        self.db.delete(table='document', params={'document_id': document['document_id']})
        drive.delete_file(document['file_info']['id'])
        return {'status': 'success'}
    
    @handle_exception
    def upload_file(self, file_name, mime_type, file_data, parent_folder_id, document_info, uploader):

        file_info = drive.upload_file(file_name=file_name, mime_type=mime_type, file_data=file_data, parent_folder_id=parent_folder_id)
        file_info = json.loads(file_info.data.decode("utf-8"))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        document = Document(
            document_id=timestamp,
            document_info=document_info,
            file_info=file_info,
            uploader=uploader
        )
        
        self.db.create(table='document', data=document.to_dict())
        return {'status': 'success'}