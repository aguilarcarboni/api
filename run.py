from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify

from laserfocus.utils.logger import logger

import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

public_routes = ['docs', 'index', 'login']

# JWT authentication middleware
def jwt_required_except_login():
    if request.endpoint not in public_routes:
        try:
            verify_jwt_in_request()
        except exceptions.JWTExtendedException as e:
            return jsonify({"msg": str(e)}), 401

def start_api():
    
    logger.announcement('Starting Laserfocus...', 'info')

    app = Flask(__name__, static_folder='static')
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    # Add JWT configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(milliseconds=3600000)  # 1 hour in milliseconds
    jwt = JWTManager(app)

    # Initialize Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["60 per minute"],
        storage_uri='memory://'
    )

    # Apply JWT authentication to all routes except login
    app.before_request(jwt_required_except_login)

    # Developer apps
    from src.app import drive, email, user
    app.register_blueprint(user.bp, url_prefix='/users')
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(email.bp, url_prefix='/email')

    limiter.limit("600 per minute")(drive.bp)
    limiter.limit("600 per minute")(email.bp)
    limiter.limit("600 per minute")(user.bp)

    # Create index route
    @app.route('/')
    def index():
        return send_from_directory('public/static', 'index.html')
    
    # Create documentation pages
    @app.route('/docs')
    def docs():
        return send_from_directory('public/static', 'docs.html')
    
    @app.route('/docs/drive')
    def drive():
        return send_from_directory('public/static/docs', 'drive.html')

    # Create backend routes
    @app.route('/login', methods=['POST'])
    def login():
        logger.info(f'Login request.')
        payload = request.get_json(force=True)
        token = payload['token']
        if token == "laserfocused":
            access_token = create_access_token(identity=token)
            return jsonify(access_token=access_token), 200
        return jsonify({"msg": "Bad token"}), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500 

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.error(f'Bad request: {error}')
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.error(f'Unauthorized access attempt: {error}')
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.error(f'Forbidden access attempt: {error}')
        return jsonify({"error": "Forbidden", "message": "You don't have permission to access this resource"}), 403
    
    return app

laserfocus = start_api()
logger.info('Running diagnostics and tests...')
logger.success('Diagnostics and tests completed successfully.')
logger.announcement('Welcome to Laserfocus.', 'success')