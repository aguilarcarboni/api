from flask import Blueprint, request, send_file
from io import BytesIO
import laserfocus

bp = Blueprint('drive', __name__)

@bp.route('/drive/query_files', methods=['POST'])
async def drive_query_many():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive
    response = Drive.queryForFiles(input_json['path'])
    return response

@bp.route('/drive/query_file', methods=['POST'])
async def drive_query_file():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive

    if input_json['file_name'].endswith('.xlsx') or input_json['file_name'].endswith('.csv'):
        mimetype="text/plain"
    else:
        return {'status':'error', 'content':'File type not supported.'}

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])
    response = Drive.downloadFile(response['content']['id'])
    f = BytesIO(response['content'])

    return send_file(f, mimetype=mimetype)

@bp.route('/drive/query_id', methods=['POST'])
async def drive_query_id():

    # Athena input
    input_json = request.get_json(force=True)
    Drive = laserfocus.Drive

    response = Drive.queryForFile(input_json['path'], input_json['file_name'])

    return response