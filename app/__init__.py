from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config

# Initialisation des extensions (une seule fois)
db = SQLAlchemy() # Doit être la SEULE instance de SQLAlchemy
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Route pour la page de login
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__) # crée l'application
    app.config.from_object(Config) # la configure
    # initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Enregistre les blueprints dans l'application
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.maps import maps_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(maps_bp)

    return app
