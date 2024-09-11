from flask import Blueprint, request, send_file
from io import BytesIO
from laserfocus import Drive

bp = Blueprint('drive', __name__)

Drive = Drive()

@bp.route('/drive/query_files', methods=['POST'])
async def drive_query_files():
    input_json = request.get_json(force=True)
    response = Drive.queryFilesInFolder(input_json['path'])
    return response

@bp.route('/drive/query_file', methods=['POST'])
async def drive_query_file():
    input_json = request.get_json(force=True)
    response = Drive.queryFile(input_json['path'], input_json['file_name'])
    return response

@bp.route('/drive/download_file', methods=['POST'])
async def drive_download_file():
    input_json = request.get_json(force=True)
    if input_json['file_name'].endswith('.xlsx') or input_json['file_name'].endswith('.csv'):
        mimetype="text/plain"
    else:
        return {'status':'error', 'content':'File type not supported.'}
    response = Drive.queryFile(input_json['path'], input_json['file_name'])
    response = Drive.downloadFile(response['content']['id'])
    f = BytesIO(response['content'])
    return send_file(f, mimetype=mimetype)

@bp.route('/drive/upload_file_with_path', methods=['POST'])
async def drive_upload_file_path():
    input_json = request.get_json(force=True)
    response = Drive.uploadFileWithPath(input_json['file_path'], input_json['parent_folder_id'])
    return response

@bp.route('/drive/upload_file', methods=['POST'])
async def drive_upload_file():
    input_json = request.get_json(force=True)
    response = Drive.uploadFile(input_json['file_name'], input_json['raw_file'], input_json['parent_folder_id'])
    return response

@bp.route('/drive/delete_file', methods=['POST'])
async def drive_delete_file():
    input_json = request.get_json(force=True)
    response = Drive.deleteFiles(input_json['file_ids'])
    return response

@bp.route('/drive/create_folder', methods=['POST'])
async def drive_create_folder():
    input_json = request.get_json(force=True)
    response = Drive.createFolder(input_json['folder_name'], input_json['parent_folder_id'])
    return response