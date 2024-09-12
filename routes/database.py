
from flask import request
from laserfocus import Database

from flask import Blueprint

import json
from bson import json_util

bp = Blueprint('database', __name__)

Database = Database()

@bp.route('/database/get_databases', methods=['GET'])
async def mongo_get_databases():
    response = Database.getDatabases()
    return response

@bp.route('/database/get_tables_in_database', methods=['POST'])
async def mongo_get_tables_in_database():
    input_json = request.get_json(force=True)
    response = Database.getTablesInDatabase(input_json['database'])
    return response


@bp.route('/database/query', methods=['POST'])
async def mongo_query():
    input_json = request.get_json(force=True)
    response = Database.queryDocumentInCollection(input_json['database'], input_json['table'], input_json['query'])
    return json.loads(json_util.dumps(response))

@bp.route('/database/query_many', methods=['POST'])
async def mongo_query_many():
    input_json = request.get_json(force=True)
    response = Database.queryDocumentsInCollection(input_json['database'], input_json['table'], input_json['query'])
    return json.loads(json_util.dumps(response))

@bp.route('/database/insert', methods=['POST'])
async def mongo_insert():
    input_json = request.get_json(force=True)
    response = Database.insertDocumentToCollection(input_json['database'], input_json['table'], input_json['data'], input_json['context'])
    return response

@bp.route('/database/delete', methods=['POST'])
async def mongo_delete():
    input_json = request.get_json(force=True)
    response = Database.deleteDocumentInCollection(input_json['database'], input_json['table'], input_json['query'])
    return response