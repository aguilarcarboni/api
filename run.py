from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
import os
import logging
from flask import jsonify
from logging.handlers import RotatingFileHandler

from app.helpers.logger import logger

from dotenv import load_dotenv
load_dotenv()

def jwt_required_except_login():
    if request.endpoint != 'login' and request.endpoint != 'index':
        try:
            verify_jwt_in_request()
        except exceptions.JWTExtendedException as e:
            return jsonify({"msg": str(e)}), 401
        
def configure_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    logger.info('API startup')

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    app.before_request(jwt_required_except_login)

    from app.routes import database, explorer, news, wallet, market, drive
    app.register_blueprint(drive.bp, url_prefix='/drive')
    app.register_blueprint(database.bp, url_prefix='/database')
    app.register_blueprint(explorer.bp, url_prefix='/explorer')
    app.register_blueprint(news.bp, url_prefix='/news')
    app.register_blueprint(wallet.bp, url_prefix='/wallet')
    app.register_blueprint(market.bp, url_prefix='/market')
    #app.register_blueprint(home.bp)

    @app.route('/', methods=['GET'])
    def index():
        logger.info('User accessed the root route.')
        data = {
            'title': 'the path to success starts with laserfocus.',
        }
        return jsonify(data)

    @app.route('/login', methods=['POST'])
    def login():
        payload = request.get_json(force=True)
        logger.info(f'User attempting to log in... {payload}')
        token = payload['token']
        if token == 'laserfocused':
            access_token = create_access_token(identity=token)
            logger.success(f'User logged in successfully. Token: {token}')
            return {"access_token": access_token}, 200
        logger.error(f'User failed to log in. Token: {token}')
        return {"msg": "Invalid token"}, 401
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500 

    return app

laserfocus = create_app()
