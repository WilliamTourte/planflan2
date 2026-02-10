"""Module principal de l'application PlanFlan.

Ce module initialise l'application Flask et configure les extensions nécessaires.
Il contient également les fonctions de sécurité et les filtres Jinja personnalisés.
"""

# Import du module os pour récupérer les variables d'environnement
import os

from flask import Flask
from sqlalchemy import text

from .config import Config  # Import relatif
from .outils import enlever_accents
from .extensions import db, migrate, login_manager, bcrypt, csrf
from .security_headers import init_security_headers
from .logging_config import (
    configure_logging,
    log_request_info,
    configure_error_handling,
)
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.maps import maps_bp
from .routes.photos import photos_bp

# Configuration du login manager
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."


def create_app(config_class=None):
    """
    Fonction principale de l'application.
    Deux configurations possibles :
        - dev
        - prod
    Vérification de la variable d'environnement FLASK_CONFIG pour le chargement de l'environnement.
    """

    if config_class is None:
        config_name = os.getenv("FLASK_CONFIG", "Config")  # Par défaut : Config (dev)
        config_class = getattr(
            __import__("app." + config_name.lower(), fromlist=["Config"]), config_name
        )

    # Vérification de la configuration utilisée
    print(f" Configuration utilisée : {config_class}")

    # Création de l'application Flask
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

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

        return db.session.get(Utilisateur, int(user_id))

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
    init_security_headers(app)

    # Configurer la journalisation
    configure_logging(app)
    log_request_info(app)
    configure_error_handling(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(photos_bp)

    # Enregistrer le blueprint API du dashboard
    from .routes.api.dashboard import dashboard_api_bp

    app.register_blueprint(dashboard_api_bp)

    return app
