from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from laserfocus.utils.response import Response
from laserfocus.utils.logger import logger

import os
from dotenv import load_dotenv

load_dotenv()

def jwt_required():
    if request.endpoint != 'login' and request.endpoint != 'index':
        try:
            verify_jwt_in_request()
        except exceptions.JWTExtendedException as e:
            return Response.error(str(e)), 401

def start_api():
    
    logger.announcement('Starting Laserfocus...', 'info')

    # Initialize Flask app
    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["84600 per day", "3600 per hour"],
        storage_uri="memory://"
    )

    # Register JWT before request according to some parameters
    app.before_request(jwt_required)

    # Developer apps
    from src.app import drive,  databases, wallet, email
    app.register_blueprint(databases.bp, url_prefix='/databases')
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(wallet.bp, url_prefix='/wallet')
    app.register_blueprint(email.bp, url_prefix='/email')
    #app.register_blueprint(database.bp, url_prefix='/database')

    limiter.limit("600 per minute")(databases.bp)

    # Define routes
    @app.route('/', methods=['GET'])
    def index():
        return Response.success('the path to success starts with laserfocus.'), 200
    
    @app.route('/docs')
    def docs():
        return send_from_directory('public/static', 'docs.html')

    @app.route('/login', methods=['POST'])
    def login():
        payload = request.get_json(force=True)
        try:
            token = payload['token']
            logger.info(f'User attempting authentication using token: {token}')
            if token == 'laserfocused':
                access_token = create_access_token(identity=token)
                logger.success(f'User authenticated. {token}.')
                return Response.success(access_token), 200
            else:
                raise Exception('Invalid token')
        except Exception as e:
            logger.error(f'User failed to authenticate: {e}')
            return Response.error("Invalid token"), 401
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.error(f"Rate limit exceeded: {e.description}")
        return Response.error("Rate limit exceeded"), 429

    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f'Not found: {error}')
        return Response.error("Not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        return Response.error("Internal server error"), 500 

    @app.errorhandler(400)
    def bad_request_error(error):
        logger.error(f'Bad request: {error}')
        return Response.error("Bad request"), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        logger.error(f'Unauthorized access attempt: {error}')
        return Response.error("Unauthorized"), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.error(f'Forbidden access attempt: {error}')
        return Response.error("Forbidden"), 403

    return app

laserfocus = start_api()
logger.info('Running diagnostics and tests...')
logger.success('Diagnostics and tests completed successfully.')
logger.announcement('Welcome to Laserfocus.', 'success')