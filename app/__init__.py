from flask import Flask, has_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.outils import enlever_accents
from flask_migrate import Migrate

# Initialisation des extensions (une seule fois)
db = SQLAlchemy()  # Doit être la SEULE instance de SQLAlchemy
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Route pour la page de login
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)  # crée l'application
    app.config.from_object(Config)  # la configure

    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Enregistrement du context processor
    @app.context_processor
    def inject_forms():
        from app.forms import DeleteForm, ValidateForm
        print("Context processor appelé !")  # <-- Log
        delete_form = DeleteForm()
        validate_form = ValidateForm() if has_request_context() and current_user.is_authenticated and hasattr(
            current_user, 'is_admin') and current_user.is_admin else None
        print(f"delete_form = {delete_form}, validate_form = {validate_form}")
        return dict(delete_form=delete_form, validate_form=validate_form)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Utilisateur
        return Utilisateur.query.get(int(user_id))

    @app.template_filter('enlever_accents')  # filtre Jinja2 pour enlever les accents
    def filtre_enlever_accents(text):
        return enlever_accents(text)

    # Enregistre les blueprints dans l'application
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.maps import maps_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(maps_bp)

    return app
