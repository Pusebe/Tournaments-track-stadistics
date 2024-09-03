from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy_utils import database_exists, create_database
import os

db = SQLAlchemy()
DB_NAME = 'sqlite:///database.db'
UPLOAD_FOLDER = "/static/images/"

'''
db = SQLAlchemy()
DB_USER = 'admin'
DB_HOST = 'database-2.cfukvkttheie.eu-north-1.rds.amazonaws.com'
DB_PORT = '3306'
DB_NAME = 'mysql+pymysql://' + DB_USER + ':' + os.environ.get('DB_PASSWORD') + '@' + DB_HOST + ':' + DB_PORT + '/envite'
UPLOAD_FOLDER = "/static/images/"
'''

# Configuración de la base de datos
DB_USER = 'root'
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')  # Contraseña del usuario root
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'envite'  # Nombre de tu base de datos

# Cadena de conexión
DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

UPLOAD_FOLDER = "/static/images/"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_NAME
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    from .views import views
    from .auth import auth
    #from .game_views import game_views

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    #app.register_blueprint(game_views, url_prefix='/game')

    from .models import User

    with app.app_context():
        if not database_exists(db.engine.url):
            create_database(db.engine.url)
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Necesitas estar logueado para poder poder entrar aquí."
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def register_error_handlers(app):
        @app.errorhandler(404)
        def error_404_handler(e):
            flash(
                'La url a la que intentabas acceder no está disponible, error 404', category='error')
            return redirect(url_for('views.home'))

    register_error_handlers(app)
    return app


# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app=app)
#         print('Created Database!')
