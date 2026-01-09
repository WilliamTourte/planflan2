"""Module principal de l'application PlanFlan.

Ce module initialise l'application Flask et configure les extensions nécessaires.
Il contient également les fonctions de sécurité et les filtres Jinja personnalisés.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from .config import Config  # Import relatif
from .outils import enlever_accents
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(config_class=Config):
    """Crée et configure l'application Flask.

    Args:
        config_class: La classe de configuration à utiliser

    Returns:
        Flask: L'application Flask configurée
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    from sqlalchemy import text

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print(
                "Connexion reussie avec l'URL :",
                app.config["SQLALCHEMY_DATABASE_URI"],
            )
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            print(f"URL utilisee : {app.config['SQLALCHEMY_DATABASE_URI']}")

    @login_manager.user_loader
    def load_user(user_id):
        """Charge un utilisateur à partir de son ID.

        Args:
            user_id (int): L'ID de l'utilisateur à charger

        Returns:
            Utilisateur: L'objet utilisateur correspondant ou None si non trouvé
        """
        from .models import Utilisateur

        return Utilisateur.query.get(int(user_id))

    @app.template_filter("enlever_accents")
    def filtre_enlever_accents(text):
        """Filtre Jinja pour enlever les accents d'un texte.

        Args:
            text (str): Le texte à traiter

        Returns:
            str: Le texte sans accents
        """
        return enlever_accents(text)

    # Initialiser les en-têtes de sécurité
    from .security_headers import init_security_headers

    init_security_headers(app)

    # Configurer la journalisation
    from .logging_config import (
        configure_logging,
        log_request_info,
        configure_error_handling,
    )

    configure_logging(app)
    log_request_info(app)
    configure_error_handling(app)

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.maps import maps_bp
    from .routes.photos import photos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(photos_bp)

    return app
