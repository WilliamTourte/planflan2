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
                "✅ Connexion réussie avec l'URL :",
                app.config["SQLALCHEMY_DATABASE_URI"],
            )
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")
            print(f"URL utilisée : {app.config['SQLALCHEMY_DATABASE_URI']}")

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

    # Ajouter des en-têtes de sécurité
    @app.after_request
    def add_security_headers(response):
        """Ajoute des en-têtes de sécurité HTTP à toutes les réponses.
        
        Cette fonction configure la Content Security Policy (CSP) et d'autres
        en-têtes de sécurité pour protéger l'application contre les attaques
        courantes comme XSS, clickjacking, etc.
        
        Args:
            response: L'objet réponse Flask à modifier
            
        Returns:
            response: L'objet réponse avec les en-têtes de sécurité ajoutés
        """
        # Content Security Policy - à adapter selon vos besoins
        # Autorise les ressources nécessaires pour l'application:
        # - cdn.jsdelivr.net pour Bootstrap et autres bibliothèques
        # - unpkg.com pour Leaflet
        # - maps.googleapis.com pour Google Maps
        # - 'unsafe-inline' nécessaire pour certains scripts et styles
        csp = (
            "default-src 'self' http://localhost; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net unpkg.com "
            "maps.googleapis.com http://localhost; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net unpkg.com "
            "http://localhost; "
            "img-src 'self' data: cdn.jsdelivr.net maps.googleapis.com "
            "unpkg.com maps.gstatic.com a.tile.openstreetmap.org "
            "b.tile.openstreetmap.org c.tile.openstreetmap.org; "
            "font-src 'self' cdn.jsdelivr.net; "
            "connect-src 'self' cdn.jsdelivr.net unpkg.com "
            "maps.googleapis.com http://localhost; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self' http://localhost"
        )

        response.headers["Content-Security-Policy"] = csp
        # Pour les navigateurs modernes, ajouter une Permission Policy pour la géolocalisation

        # En développement, autoriser aussi localhost
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), microphone=(), camera=()"
        )

        # X-Frame-Options pour prévenir le clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # X-Content-Type-Options pour prévenir le MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Strict-Transport-Security (uniquement en production avec HTTPS)
        if not app.debug and app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.maps import maps_bp
    from .routes.photos import photos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(photos_bp)

    return app
