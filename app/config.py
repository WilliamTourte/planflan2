"""Module de configuration de l'application PlanFlan.

Ce module contient les classes de configuration pour les différents environnements
de l'application, incluant les paramètres de base de données, les clés secrètes,
et les configurations spécifiques aux tests.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base pour l'application.

    Cette classe définit les paramètres de configuration communs à tous les
    environnements, tels que les clés secrètes, les URI de base de données,
    et les paramètres de sécurité.
    """

    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Utiliser SQLite par défaut si DATABASE_URL n'est pas défini ou si MySQL n'est pas disponible
    db_url = os.getenv("DATABASE_URL")
    if not db_url or db_url.startswith("mysql://"):
        # Vérifier si nous pouvons nous connecter à MySQL, sinon utiliser SQLite
        try:
            import pymysql
            from sqlalchemy import create_engine
            try:
                # Tester la connexion MySQL
                test_url = db_url or "mysql+pymysql://root:@localhost/planflan_db"
                engine = create_engine(test_url)
                with engine.connect() as conn:
                    pass  # Si on arrive ici, la connexion fonctionne
                SQLALCHEMY_DATABASE_URI = test_url
            except Exception:
                print("MySQL non disponible, utilisation de SQLite...")
                SQLALCHEMY_DATABASE_URI = "sqlite:///planflan.db"
        except ImportError:
            print("PyMySQL non installé, utilisation de SQLite...")
            SQLALCHEMY_DATABASE_URI = "sqlite:///planflan.db"
    else:
        SQLALCHEMY_DATABASE_URI = db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Active le logging des requêtes SQL
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 3600
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    UPLOAD_FOLDER = "app/static/uploads"
    LOG_LEVEL = "DEBUG"  # Active le niveau DEBUG pour voir tous les logs


class TestConfig(Config):
    """Configuration spécifique pour les tests.

    Cette classe hérite de Config et redéfinit certains paramètres pour
    faciliter les tests, comme l'utilisation d'une base de données en mémoire
    et la désactivation de la protection CSRF.
    """

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key-for-testing-purposes-only"

    # Configuration des uploads pour les tests
    UPLOAD_FOLDER = "app/static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo
