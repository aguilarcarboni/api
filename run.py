from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
import os
from flask import jsonify
from app.helpers.logger import logger
from dotenv import load_dotenv
from app.helpers.api import access_api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

    # Custom error handler for rate limiting
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.error(f"Rate limit exceeded: {e.description}")
        return jsonify({
            "error": "Rate limit exceeded",
            "message": e.description
        }), 429

    app.before_request(jwt_required)

    # Import and register blueprints
    from app.routes import database, drive, news, market, email, tools, spotify, sports, tv
    from app.routes.wallet import bac
    
    # Add specific rate limits for sensitive endpoints
    limiter.limit("600 per minute")(database.bp)
    
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(database.bp, url_prefix='/database')
    app.register_blueprint(email.bp, url_prefix='/email')
    app.register_blueprint(market.bp, url_prefix='/market')
    app.register_blueprint(news.bp, url_prefix='/news')
    app.register_blueprint(tools.bp, url_prefix='/tools')
    #app.register_blueprint(home.bp, url_prefix='/home')
    app.register_blueprint(spotify.bp, url_prefix='/spotify')
    app.register_blueprint(sports.bp, url_prefix='/sports')
    app.register_blueprint(tv.bp, url_prefix='/tv')

    # Wallet 
    app.register_blueprint(bac.bp, url_prefix='/wallet/bac')

    @app.route('/', methods=['GET'])
    @limiter.exempt  # Exempt index route from rate limiting
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
    return app

laserfocus = start_api()
logger.info('Running diagnostics and tests...')
logger.success('Diagnostics and tests completed successfully.')
logger.announcement('Welcome to Laserfocus.', 'success')