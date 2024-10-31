from flask import Flask, render_template
from flask_restful import Api
from app.modules.google import cache

def create_app():
    app = Flask(__name__)

    api = Api(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    cache.init_app(app)

    return app