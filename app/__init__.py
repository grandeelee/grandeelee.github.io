from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)  #__name__ = __main__
    app.secret_key = "2g3hjkrfhjk34hj"  # necessary for the session cookie

    app.config['MONGODB_SETTINGS'] = [
        {
            'host': 'localhost',
            'port': 27017,
            'db': 'my_db'
        }
    ]
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.static_folder = "assets"

    my_db = MongoEngine(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    return app, my_db, login_manager

app, my_db, login_manager = create_app()

from auth import auth
app.register_blueprint(auth)

from book import book
app.register_blueprint(book)
