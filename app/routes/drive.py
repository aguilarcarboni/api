from flask import Blueprint, request, send_file, current_app
from io import BytesIO
from werkzeug.utils import secure_filename
from app.modules.drive import queryFilesInFolder, queryFile, downloadFile, uploadFile, deleteFiles, createFolder
from app.helpers.response import Response
import os
from app.helpers.file_validation import is_allowed_file, get_file_mimetype
from app.helpers.logger import logger

bp = Blueprint('drive', __name__)

@bp.route('/drive/query_files', methods=['POST'])
def drive_query_files():
    input_json = request.get_json(force=True)
    return queryFilesInFolder(path=input_json['path'])

@bp.route('/drive/query_file', methods=['POST'])
def drive_query_file():
    input_json = request.get_json(force=True)
    return queryFile(input_json['path'], input_json['file_name'])

@bp.route('/drive/download_file', methods=['POST'])
def drive_download_file():
    input_json = request.get_json(force=True)
    file_name = secure_filename(input_json['file_name'])
    
    if not is_allowed_file(file_name):
        return Response.error('File type not supported.')
    
    mimetype = get_file_mimetype(file_name)
    
    # Check if file exists in cache
    logger.info(f"Checking if file exists in cache: {file_name}")
    cache_path = os.path.join('cache', 'drive', file_name)
    if os.path.exists(cache_path):
        logger.success(f"File found in cache: {file_name}")
        with open(cache_path, 'rb') as cached_file:
            return send_file(
                BytesIO(cached_file.read()),
                mimetype=mimetype,
                max_age=0
            )
    
    # If not in cache, query and download from Drive
    query_response = queryFile(input_json['path'], file_name)
    if query_response['status'] != 'success':
        return query_response

    download_response = downloadFile(query_response['content']['id'])
    if download_response['status'] != 'success':
        return download_response
    
    # Save to cache
    logger.info(f"Saving file to cache: {file_name}")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'wb') as cache_file:
        cache_file.write(download_response['content'])
    
    logger.success(f"Successfully downloaded and cached file: {file_name}")
    return send_file(
        BytesIO(download_response['content']),
        mimetype=mimetype,
        max_age=0
    )

@bp.route('/drive/upload_file', methods=['POST'])
def drive_upload_file():
    if 'file' not in request.files:
        return Response.error('No file part in the request.')
    
    file = request.files['file']
    if file.filename == '':
        return Response.error('No file selected for uploading.')
    
    filename = secure_filename(file.filename)
    if not is_allowed_file(filename):
        return Response.error('File type not allowed.')
    
    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
        return Response.error('File size exceeds the limit.')
    
    parent_folder_id = request.form.get('parent_folder_id')
    
    return uploadFile(filename, file, parent_folder_id)

@bp.route('/drive/delete_file', methods=['POST'])
def drive_delete_file():
    input_json = request.get_json(force=True)
    return deleteFiles(input_json['file_ids'])

@bp.route('/drive/create_folder', methods=['POST'])
def drive_create_folder():
    input_json = request.get_json(force=True)
    folder_name = secure_filename(input_json['folder_name'])
    return createFolder(folder_name, input_json['parent_folder_id'])