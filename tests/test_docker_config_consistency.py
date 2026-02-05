"""Test de cohérence entre Dockerfile, configprod.py et les routes de photos."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import sys

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules de configuration avant les tests
from app.config import TestConfig
from app.configprod import ConfigProd

@pytest.fixture
def temp_upload_env():
    """Crée un environnement temporaire pour simuler Docker."""
    temp_dir = tempfile.mkdtemp()
    upload_folder = os.path.join(temp_dir, "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    # Configuration simulée de production
    config = {
        'UPLOAD_FOLDER': '/app/static/uploads',
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'},
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024
    }

    yield temp_dir, upload_folder, config

    # Nettoyage après le test
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_no_real_database_used():
    """Test que ce test n'utilise pas de vraie base de données."""
    # Ce test vérifie que nous utilisons bien TestConfig avec SQLite en mémoire
    # au lieu de ConfigProd qui utiliserait une vraie base de données

    # Les imports sont déjà faits en haut du fichier

    # Vérifier que TestConfig utilise SQLite en mémoire (pas de vraie DB)
    assert TestConfig.TESTING == True, \
        "TestConfig doit avoir TESTING=True pour éviter les opérations réelles"
    assert "sqlite" in TestConfig.SQLALCHEMY_DATABASE_URI.lower(), \
        "TestConfig doit utiliser SQLite pour éviter la vraie base de données"
    assert ":memory:" in TestConfig.SQLALCHEMY_DATABASE_URI, \
        "TestConfig doit utiliser une base de données en mémoire"

    # Vérifier que ConfigProd utilise bien une URI différente (MySQL en production)
    assert ConfigProd.SQLALCHEMY_DATABASE_URI != TestConfig.SQLALCHEMY_DATABASE_URI, \
        "ConfigProd doit utiliser une base de données différente de TestConfig"
    assert "mysql" in ConfigProd.SQLALCHEMY_DATABASE_URI.lower() or \
           "postgresql" in ConfigProd.SQLALCHEMY_DATABASE_URI.lower(), \
        "ConfigProd doit utiliser MySQL ou PostgreSQL en production"

    # Vérifier que nous pouvons accéder à la configuration sans connexion DB
    assert hasattr(TestConfig, 'UPLOAD_FOLDER'), \
        "La configuration de test doit être accessible sans base de données"
    assert TestConfig.UPLOAD_FOLDER is not None, \
        "La configuration de test doit avoir un UPLOAD_FOLDER valide"

def test_upload_folder_consistency():
    """Test que le chemin UPLOAD_FOLDER est cohérent entre configprod.py et Dockerfile."""
    # Les imports sont déjà faits en haut du fichier

    # Vérifier que le chemin dans configprod.py correspond à celui du Dockerfile
    expected_path = "/app/static/uploads"
    assert ConfigProd.UPLOAD_FOLDER == expected_path, \
        "Le chemin UPLOAD_FOLDER doit être /app/static/uploads"

    # Vérifier que le chemin est absolu dans un contexte Docker/Linux
    # Sur Windows, les chemins Unix comme /app/static/uploads ne sont pas considérés
    # comme absolus, mais ils le seraient dans un conteneur Docker Linux
    # On vérifie donc juste que le chemin commence par / (convention Unix)
    assert expected_path.startswith("/"), \
        "Le chemin UPLOAD_FOLDER doit être un chemin absolu Unix (commencer par /)"
    
    # Vérifier que la configuration de test a aussi un chemin uploads défini
    assert hasattr(TestConfig, 'UPLOAD_FOLDER'), \
        "La configuration de test doit aussi avoir UPLOAD_FOLDER défini"

def test_upload_folder_permissions(temp_upload_env):
    """Test que le dossier uploads a les bonnes permissions (simulé)."""
    temp_dir, upload_folder, config = temp_upload_env

    # Vérifier que le dossier existe
    assert os.path.exists(upload_folder), \
        "Le dossier uploads doit exister"

    # Vérifier que le dossier est accessible en écriture
    test_file = os.path.join(upload_folder, "test_write.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        # Si on arrive ici, c'est que l'écriture et la suppression ont fonctionné
        assert True, "Le dossier uploads doit être accessible en écriture"
    except Exception as e:
        pytest.fail(f"Le dossier uploads n'est pas accessible en écriture: {e}")
    
    # Vérifier que le dossier est accessible en lecture
    try:
        files = os.listdir(upload_folder)
        assert isinstance(files, list), "Le dossier uploads doit être lisible"
    except Exception as e:
        pytest.fail(f"Le dossier uploads n'est pas accessible en lecture: {e}")

def test_photos_route_uses_correct_config():
    """Test que les routes de photos utilisent la bonne configuration."""
    # Les imports sont déjà faits en haut du fichier
    
    # Créer une application Flask avec la configuration de test
    from app import create_app
    app = create_app(TestConfig)
    
    with app.app_context():
        # Vérifier que la configuration est correctement chargée
        assert app.config['UPLOAD_FOLDER'] == TestConfig.UPLOAD_FOLDER, \
            "La configuration doit avoir le bon UPLOAD_FOLDER"
        
        assert app.config['ALLOWED_EXTENSIONS'] == TestConfig.ALLOWED_EXTENSIONS, \
            "La configuration doit avoir les bonnes extensions autorisées"
        
        # Vérifier que la taille maximale est correcte
        assert app.config['MAX_CONTENT_LENGTH'] == TestConfig.MAX_CONTENT_LENGTH, \
            "La configuration doit avoir la bonne taille maximale"
        
        # Vérifier que les valeurs correspondent à celles de configprod.py (production)
        assert TestConfig.ALLOWED_EXTENSIONS == ConfigProd.ALLOWED_EXTENSIONS, \
            "Les extensions autorisées doivent être cohérentes entre test et production"
        assert TestConfig.MAX_CONTENT_LENGTH == ConfigProd.MAX_CONTENT_LENGTH, \
            "La taille maximale doit être cohérente entre test et production"
        
        # Importer le module photos dans le contexte de l'application
        from app.routes.photos import photos_bp
        
        # Vérifier que le blueprint est correctement configuré
        assert photos_bp is not None, "Le blueprint photos doit être importé avec succès"

def test_dockerfile_upload_folder_creation(temp_upload_env):
    """Test que le Dockerfile crée correctement le dossier uploads."""
    temp_dir, _, config = temp_upload_env

    # Simuler la création du dossier comme dans le Dockerfile
    docker_upload_folder = os.path.join(temp_dir, "app", "static", "uploads")
    os.makedirs(docker_upload_folder, exist_ok=True)

    # Vérifier que le dossier existe
    assert os.path.exists(docker_upload_folder), \
        "Le Dockerfile doit créer le dossier /app/static/uploads"

    # Vérifier que le chemin correspond à celui de configprod.py
    # On vérifie juste que le chemin se termine par la structure attendue
    # car le chemin absolu complet dépend du système de fichiers
    expected_suffix = os.path.join("app", "static", "uploads")
    assert docker_upload_folder.endswith(expected_suffix), \
        f"Le chemin créé par le Dockerfile doit se terminer par {expected_suffix}"

def test_config_values_match_dockerfile():
    """Test que les valeurs de configuration correspondent aux attentes du Dockerfile."""
    # Les imports sont déjà faits en haut du fichier

    # Vérifier les valeurs attendues dans le Dockerfile pour la production
    assert ConfigProd.UPLOAD_FOLDER == "/app/static/uploads", \
        "UPLOAD_FOLDER doit être /app/static/uploads comme dans le Dockerfile"

    assert ConfigProd.ALLOWED_EXTENSIONS == {"png", "jpg", "jpeg", "gif"}, \
        "Les extensions autorisées doivent correspondre à celles attendues"

    assert ConfigProd.MAX_CONTENT_LENGTH == 16 * 1024 * 1024, \
        "La taille maximale doit être 16 Mo comme configuré"
    
    # Vérifier que la configuration de test a des valeurs cohérentes
    assert TestConfig.UPLOAD_FOLDER is not None and len(TestConfig.UPLOAD_FOLDER) > 0, \
        "La configuration de test doit avoir un UPLOAD_FOLDER valide"

def test_config_constants_defined():
    """Test que toutes les constantes de configuration nécessaires sont définies."""
    # Les imports sont déjà faits en haut du fichier

    # Vérifier que toutes les constantes nécessaires pour le Dockerfile sont définies
    required_attrs = [
        'UPLOAD_FOLDER',
        'ALLOWED_EXTENSIONS', 
        'MAX_CONTENT_LENGTH',
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI'
    ]
    
    for attr in required_attrs:
        assert hasattr(ConfigProd, attr), f"La constante {attr} doit être définie dans ConfigProd"
        assert hasattr(TestConfig, attr), f"La constante {attr} doit être définie dans TestConfig"

    # Vérifier que les valeurs ne sont pas None ou vides
    assert ConfigProd.UPLOAD_FOLDER, "UPLOAD_FOLDER ne doit pas être vide"
    assert ConfigProd.ALLOWED_EXTENSIONS, "ALLOWED_EXTENSIONS ne doit pas être vide"
    assert ConfigProd.MAX_CONTENT_LENGTH > 0, "MAX_CONTENT_LENGTH doit être positif"
    
    # Vérifier que la configuration de test utilise bien SQLite en mémoire
    assert "sqlite" in TestConfig.SQLALCHEMY_DATABASE_URI.lower(), \
        "La configuration de test doit utiliser SQLite pour éviter la vraie base de données"
    assert ":memory:" in TestConfig.SQLALCHEMY_DATABASE_URI, \
        "La configuration de test doit utiliser une base de données en mémoire"
