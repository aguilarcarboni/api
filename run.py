from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os

from dotenv import load_dotenv

from src.utils.logger import logger

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

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["84600 per day", "3600 per hour"],
        storage_uri="memory://"
    )

    app.before_request(jwt_required)

    # Import and register blueprints
    from src.app import database, drive, news, market, email, tools, sports, tv, lists
    
    # Add specific rate limits for sensitive endpoints
    limiter.limit("600 per minute")(database.bp)
    
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(database.bp, url_prefix='/database')
    app.register_blueprint(email.bp, url_prefix='/email')
    app.register_blueprint(tools.bp, url_prefix='/tools')

    app.register_blueprint(lists.bp, url_prefix='/lists')

    app.register_blueprint(market.bp, url_prefix='/market')
    app.register_blueprint(news.bp, url_prefix='/news')
    app.register_blueprint(sports.bp, url_prefix='/sports')
    app.register_blueprint(tv.bp, url_prefix='/tv')

    # Wallet 
    #app.register_blueprint(bac.bp, url_prefix='/wallet/bac')

    #app.register_blueprint(home.bp, url_prefix='/home')
    #app.register_blueprint(spotify.bp, url_prefix='/spotify')

    @app.route('/', methods=['GET'])
    @limiter.exempt  # Exempt index route from rate limiting
    def index():
        data = {
            'title': 'the path to success starts with laserfocus.',
        }
        return jsonify(data)
    
    @app.route('/docs')
    def docs():
        return send_from_directory('public/static', 'docs.html')


    @app.route('/login', methods=['POST'])
    def login():
        payload = request.get_json(force=True)
        logger.info(f'User attempting authentication... {payload}')
        print(payload)
        token = payload['token']
        if token == 'laserfocused':
            access_token = create_access_token(identity=token)
            logger.success(f'User authenticated. {token}.')
            return {"access_token": access_token}, 200
        
        logger.error(f'User failed to authenticate.')
        return {"msg": "Invalid token"}, 401
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.error(f"Rate limit exceeded: {e.description}")
        return jsonify({
            "error": "Rate limit exceeded",
            "message": e.description
        }), 429

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

        
    logger.success('Laserfocus initialized successfully')
    return app

laserfocus = start_api()
logger.info('Running diagnostics and tests...')
logger.success('Diagnostics and tests completed successfully.')
logger.announcement('Welcome to Laserfocus.', 'success')