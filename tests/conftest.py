import pytest
from app import create_app, db
from app.config import TestConfig
from flask_login import login_user
from flask_bcrypt import Bcrypt

@pytest.fixture(scope='function')
def client():
    """Fixture partagée pour créer un client de test avec un utilisateur connecté"""
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Créer des données de test avec mot de passe haché
            bcrypt = Bcrypt()
            from app.models import Utilisateur
            user = Utilisateur(pseudo='testuser', email='test@example.com', is_admin=True)
            user.set_password('password', bcrypt)
            db.session.add(user)
            db.session.commit()
            
            # Vérifier que l'utilisateur a bien été créé
            created_user = Utilisateur.query.filter_by(email='test@example.com').first()
            assert created_user is not None, "L'utilisateur de test n'a pas été créé"
            assert created_user.is_admin == True, "L'utilisateur n'est pas admin"
            
            # Connexion de l'utilisateur
            login_response = client.post('/login', data=dict(
                pseudo='testuser',
                password='password'
            ), follow_redirects=True)
            
            # Vérifier que la connexion a réussi
            assert login_response.status_code == 200, f"La connexion a échoué avec le statut {login_response.status_code}"
            
            # Stocker l'utilisateur créé pour les tests
            app.config['TEST_USER'] = created_user
        yield client
        
        # Nettoyage après les tests
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='module')
def app():
    """Fixture pour l'application Flask"""
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def clean_db():
    """Fixture pour nettoyer la base de données entre les tests"""
    yield
    # Le nettoyage est géré par la fixture client
