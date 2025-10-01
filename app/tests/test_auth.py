import pytest
from app import create_app, db
from app.models import Utilisateur
from flask_bcrypt import check_password_hash

# Fixtures
@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Tests
def test_creer_utilisateur(client, app):
    data = {
        'pseudo': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword'
    }
    response = client.post('register', data=data, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = Utilisateur.query.filter_by(pseudo='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert check_password_hash(user.password, 'testpassword')  # Utilise Flask-Bcrypt

def test_connexion_utilisateur(client, app):
    # D'abord, créer un utilisateur
    data = {
        'pseudo': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword'
    }
    client.post('register', data=data, follow_redirects=True)

    # Ensuite, tester la connexion
    login_data = {
        'pseudo': 'testuser',
        'password': 'testpassword'
    }
    response = client.post('login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert '_user_id' in sess  # Vérifie que l'utilisateur est connecté
