# gunicorn -b :8080 run:laserfocus
from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import JWTManager, verify_jwt_in_request, create_access_token, exceptions
import os
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    from app.routes import main, database, explorer, weather, news, sports, wallet, market, drive
    app.register_blueprint(drive.bp)
    #app.register_blueprint(home.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(database.bp)
    app.register_blueprint(explorer.bp)
    app.register_blueprint(weather.bp)
    app.register_blueprint(news.bp)
    app.register_blueprint(sports.bp)
    app.register_blueprint(wallet.bp)
    app.register_blueprint(market.bp)
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500 

    @app.before_request
    def jwt_required_except_login():
        if request.endpoint != 'login':
            try:
                verify_jwt_in_request()
            except exceptions.JWTExtendedException as e:
                return {"msg": str(e)}, 401

    @app.route('/login', methods=['POST'])
    def login():
        payload = request.get_json(force=True)
        username = payload['token']
        if username == 'laserfocused':
            access_token = create_access_token(identity=username)
            return {"access_token": access_token}, 200
        return {"msg": "Invalid token"}, 401

    return app

laserfocus = create_app()