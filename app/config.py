import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables depuis un fichier .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'iloveflan')  # À remplacer par une clé forte en production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:password@localhost/planflan')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True  # Active les cookies sécurisés en HTTPS
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 3600  # Durée de session limitée
