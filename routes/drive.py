from flask import Blueprint, request, send_file
from io import BytesIO
from laserfocus import Drive

bp = Blueprint('drive', __name__)

Drive = Drive()

@bp.route('/drive/query_files', methods=['POST'])
async def drive_query_many():

    # Athena input
    input_json = request.get_json(force=True)
    response = Drive.queryFiles(input_json['path'])
    return response

@bp.route('/drive/query_file', methods=['POST'])
async def drive_query_file():

    # Athena input
    input_json = request.get_json(force=True)

    response = Drive.queryFile(input_json['path'], input_json['file_name'])

    return response

@bp.route('/drive/download_file', methods=['POST'])
async def drive_get_file():

    # Athena input
    input_json = request.get_json(force=True)
    
    if input_json['file_name'].endswith('.xlsx') or input_json['file_name'].endswith('.csv'):
        mimetype="text/plain"
    else:
        return {'status':'error', 'content':'File type not supported.'}

    response = Drive.queryFile(input_json['path'], input_json['file_name'])
    response = Drive.downloadFile(response['content']['id'])
    f = BytesIO(response['content'])

    return send_file(f, mimetype=mimetype)
