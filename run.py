from flask import Flask
from flask_cors import CORS

def start_laserfocus():
    
    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'

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

    return app

if __name__ == '__main__':
    app = start_laserfocus()
    debug = False
    app.run(debug=debug, host='0.0.0.0', port=5001)