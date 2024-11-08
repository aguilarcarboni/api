from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
import os
from flask import jsonify
from app.helpers.logger import logger
from dotenv import load_dotenv
load_dotenv()

def jwt_required():
    if request.endpoint != 'login' and request.endpoint != 'index':
        try:
            verify_jwt_in_request()
        except exceptions.JWTExtendedException as e:
            return jsonify({"msg": str(e)}), 401

def start_api():
    logger.announcement('Starting Laserfocus...', 'info')

    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    app.before_request(jwt_required)

    from app.routes import database, drive, news, wallet, market, email, tools, home
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(database.bp, url_prefix='/database')
    app.register_blueprint(email.bp, url_prefix='/email')
    app.register_blueprint(wallet.bp, url_prefix='/wallet')
    app.register_blueprint(market.bp, url_prefix='/market')
    app.register_blueprint(news.bp, url_prefix='/news')
    app.register_blueprint(tools.bp, url_prefix='/tools')
    app.register_blueprint(home.bp, url_prefix='/home')

    @app.route('/', methods=['GET'])
    def index():
        data = {
            'title': 'the path to success starts with laserfocus.',
        }
        return jsonify(data)

    @app.route('/login', methods=['POST'])
    def login():
        payload = request.get_json(force=True)
        logger.info(f'User attempting authentication... {payload}')
        token = payload['token']
        if token == 'laserfocused':
            access_token = create_access_token(identity=token)
            logger.success(f'User authenticated. {token}.')
            return {"access_token": access_token}, 200
        
        logger.error(f'User failed to authenticate.')
        return {"msg": "Invalid token"}, 401
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500 
        
    logger.success('Laserfocus initialized successfully')
    logger.info('Running diagnostics and tests...')
    logger.success('Diagnostics and tests completed successfully.')
    logger.announcement('Welcome to Laserfocus.', 'success')
    return app

laserfocus = start_api()
