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
    """Configuration de base"""

    # Clé secrète pour les sessions
    SECRET_KEY = os.environ.get("SECRET_KEY") or "votre-cle-secrete-ici"

    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "mysql+pymysql://flask_user:flanflask@localhost/planflan_db"
    )
    print(f" ConfigProd - database URI : {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration des sessions
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Configuration des uploads
    UPLOAD_FOLDER = "app/static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo

    # Configuration de la journalisation
    LOG_LEVEL = "INFO"

    # Configuration de la sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Configuration du cache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class ConfigProd(Config):
    """Configuration pour l'environnement de production"""

    DEBUG = False
    TESTING = False

    # Configuration de la journalisation
    LOG_LEVEL = "WARNING"

    # Configuration de la sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Configuration du cache
    CACHE_TYPE = "FileSystemCache"
    CACHE_DIR = "/tmp/flask_cache"
    CACHE_DEFAULT_TIMEOUT = 300
