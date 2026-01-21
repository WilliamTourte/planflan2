"""
Module de configuration de la journalisation pour l'application PlanFlan.

Ce module configure un système de journalisation complet avec rotation des fichiers,
niveaux de log appropriés et gestion des erreurs améliorée.
"""

import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
import traceback
from flask.logging import default_handler
from flask import request, render_template


def configure_logging(app):
    """
    Configure la journalisation pour l'application Flask.

    Cette fonction configure plusieurs handlers de log :
    - Un handler de fichier avec rotation
    - Un handler de console pour le développement
    - Un handler SMTP pour les erreurs critiques en production

    Args:
        app: L'application Flask
    """
    # Désactiver le handler par défaut de Flask pour éviter les doublons
    app.logger.removeHandler(default_handler)

    # Configurer le niveau de log global
    log_level = app.config.get("LOG_LEVEL", "INFO")
    app.logger.setLevel(log_level)

    # Créer un formatteur commun
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
    )

    # 1. Handler de fichier avec rotation
    configure_file_logging(app, formatter)

    # 2. Handler de console (uniquement en développement)
    if app.debug:
        configure_console_logging(app, formatter)

    # 3. Handler SMTP pour les erreurs critiques (uniquement en production)
    if not app.debug and not app.testing:
        configure_email_logging(app, formatter)

    # 4. Handler pour les requêtes HTTP
    configure_http_logging(app)

    # Log initial
    app.logger.info("PlanFlan application started")
    app.logger.info(f'Environment: {"DEVELOPMENT" if app.debug else "PRODUCTION"}')
    app.logger.info(f"Log level: {log_level}")


def configure_file_logging(app, formatter):
    """Configure le handler de fichier avec rotation."""
    # Créer le dossier de logs s'il n'existe pas
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configurer le handler de fichier avec rotation
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "planflan.log"),
        maxBytes=1024 * 1024 * 5,  # 5 Mo
        backupCount=10,  # Garder 10 fichiers de backup
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Ajouter un filtre pour exclure les logs de développement
    class ProductionFilter(logging.Filter):
        """Filtre de journalisation pour l'environnement de production.

        Ce filtre exclut les logs lorsque l'application est en mode debug,
        permettant ainsi de réduire le bruit dans les logs de production.
        """

        def filter(self, record):
            """Filtre les records de log.

            Args:
                record: Le record de log à filtrer

            Returns:
                bool: True si le record doit être logged, False sinon
            """
            return not app.debug

    file_handler.addFilter(ProductionFilter())
    app.logger.addHandler(file_handler)

    app.logger.info("File logging configured")


def configure_console_logging(app, formatter):
    """Configure le handler de console pour le développement."""
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)


def configure_email_logging(app, formatter):
    """Configure le handler SMTP pour les erreurs critiques."""
    # Configuration SMTP à partir des variables d'environnement
    smtp_server = app.config.get("SMTP_SERVER")
    smtp_port = app.config.get("SMTP_PORT", 587)
    smtp_username = app.config.get("SMTP_USERNAME")
    smtp_password = app.config.get("SMTP_PASSWORD")
    smtp_from = app.config.get("SMTP_FROM", "noreply@planflan.com")
    smtp_to = app.config.get("SMTP_TO", ["admin@planflan.com"])

    # Configurer le handler SMTP uniquement si toutes les informations sont disponibles
    if all([smtp_server, smtp_username, smtp_password, smtp_to]):
        try:
            mail_handler = SMTPHandler(
                mailhost=(smtp_server, smtp_port),
                fromaddr=smtp_from,
                toaddrs=smtp_to,
                subject="PlanFlan Critical Error",
                credentials=(smtp_username, smtp_password),
                secure=(),
                timeout=10,
            )
            mail_handler.setFormatter(formatter)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
            app.logger.info("SMTP logging configured for critical errors")
        except Exception as e:
            app.logger.warning(f"Failed to configure SMTP logging: {e}")
    else:
        app.logger.warning("SMTP configuration incomplete, email logging disabled")


def configure_http_logging(app):
    """Configure le logging des requêtes HTTP."""
    # Créer un logger spécifique pour les requêtes HTTP
    http_logger = logging.getLogger("http")
    http_logger.setLevel(logging.INFO)

    # Créer un handler de fichier spécifique pour les requêtes HTTP
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    http_file_handler = RotatingFileHandler(
        os.path.join(log_dir, "http_requests.log"),
        maxBytes=1024 * 1024 * 2,  # 2 Mo
        backupCount=5,  # Garder 5 fichiers de backup
        encoding="utf-8",
    )

    http_formatter = logging.Formatter(
        "%(asctime)s %(remote_addr)s %(method)s %(path)s %(status_code)s %(content_length)s"
    )
    http_file_handler.setFormatter(http_formatter)
    http_logger.addHandler(http_file_handler)

    # Remplacer le logger Werkzeug par notre logger personnalisé
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers = []

    # Créer un formatteur simple pour Werkzeug qui ne nécessite pas de champs supplémentaires
    werkzeug_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    http_file_handler.setFormatter(werkzeug_formatter)

    werkzeug_logger.addHandler(http_file_handler)
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.propagate = False  # Empêcher la propagation aux autres loggers

    app.logger.info("HTTP request logging configured")


def log_request_info(app):
    """
    Middleware pour logger les informations des requêtes HTTP.

    Args:
        app: L'application Flask
    """

    @app.after_request
    def log_request(response):
        # Récupérer le logger HTTP
        http_logger = logging.getLogger("http")

        # Extraire les informations de la requête
        remote_addr = request.remote_addr
        method = request.method
        path = request.path
        status_code = response.status_code
        content_length = response.content_length or 0
        user_agent = request.user_agent.string if request.user_agent else "Unknown"

        # Logger les informations
        http_logger.info(
            f"{remote_addr} {method} {path} {status_code} {content_length} {user_agent}"
        )

        return response


def configure_error_handling(app):
    """Configure la gestion des erreurs avec logging amélioré."""

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Gère les exceptions globales avec logging détaillé."""
        # Logger l'erreur avec des détails
        try:
            app.logger.error(
                f"Unexpected error: {str(e)}",
                exc_info=True,
                extra={
                    "status_code": 500,
                    "request_method": request.method,
                    "request_path": request.path,
                    "remote_addr": request.remote_addr,
                    "user_agent": (
                        request.user_agent.string if request.user_agent else "Unknown"
                    ),
                },
            )
        except Exception as log_error:  # pylint: disable=unused-argument
            # En cas d'erreur de logging, utiliser un message simple
            app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            app.logger.error(f"Logging error: {str(log_error)}")

        return {
            "error": f"Une erreur est survenue: {str(e)}",
            "status": "error",
            "type": type(e).__name__,
            "traceback": traceback.format_exc() if app.debug else None,
        }, 500

    @app.errorhandler(404)
    def handle_404(e):  # pylint: disable=unused-argument
        """Gère les erreurs 404 avec logging."""
        app.logger.warning(
            f"Page not found: {request.path}",
            extra={
                "status_code": 404,
                "request_method": request.method,
                "remote_addr": request.remote_addr,
            },
        )
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def handle_403(e):  # pylint: disable=unused-argument
        """Gère les erreurs 403 avec logging."""
        app.logger.warning(
            f"Forbidden access: {request.path}",
            extra={
                "status_code": 403,
                "request_method": request.method,
                "remote_addr": request.remote_addr,
            },
        )
        return {"error": "Accès interdit", "status": "error"}, 403

    app.logger.info("Enhanced error handling configured")
