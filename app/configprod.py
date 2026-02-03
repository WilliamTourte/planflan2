"""Module de configuration pour l'environnement de production.

Ce module contient les classes de configuration spécifiques à l'environnement
de production, incluant les paramètres de sécurité renforcés, les configurations
de journalisation et de cache adaptées à un déploiement en production.
"""

import os

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration de base pour l'application.

    Cette classe définit les paramètres de configuration communs à tous les
    environnements, tels que les clés secrètes, les URI de base de données,
    et les paramètres de sécurité.
    """

    # Clé secrète pour les sessions
    SECRET_KEY = os.getenv("SECRET_KEY") or "votre-cle-secrete-ici"

    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL") or "mysql+pymysql://flask_user:flanflask@localhost/planflan_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration des sessions
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Configuration des uploads
    # En production avec Docker, utiliser un chemin absolu
    UPLOAD_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
    )
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo

    # Configuration de la journalisation
    LOG_LEVEL = "INFO"

    # Configuration de la sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Configuration du cache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # Pour Google map
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    WTF_CSRF_ENABLED = True  # Explicitement activé en production
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 3600
    SQLALCHEMY_ECHO = False  # Désactivé en production


class ConfigProd(Config):
    """Configuration pour l'environnement de production"""

    DEBUG = False
    TESTING = False

    # Exiger SECRET_KEY en production - validation au chargement de la classe
    _secret_key = os.getenv("SECRET_KEY")
    if not _secret_key:
        raise ValueError(
            "SECRET_KEY doit être définie en production via la variable d'environnement"
        )
    SECRET_KEY = _secret_key

    # Exiger DATABASE_URL en production - validation au chargement de la classe
    _database_url = os.getenv("DATABASE_URL")
    if not _database_url:
        raise ValueError(
            "DATABASE_URL doit être définie en production via la variable d'environnement"
        )
    SQLALCHEMY_DATABASE_URI = _database_url

    # Configuration de la journalisation
    # Changé à INFO pour voir les logs [FETCH_PHOTOS] et diagnostiquer les problèmes de photos
    LOG_LEVEL = "INFO"

    # Configuration de la sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Configuration du cache
    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = "/tmp/flask_cache"
    CACHE_DEFAULT_TIMEOUT = 300
