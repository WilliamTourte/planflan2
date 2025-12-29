"""
Tests pour les routes d'authentification (auth.py)
"""
from app import db, bcrypt
from app.models import Utilisateur
import pytest

# Importer les fixtures depuis test_securite

@pytest.mark.auth
@pytest.mark.critical
def test_register_get(client):
    """Test la route d'inscription en GET"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Creer un compte' in response.data

@pytest.mark.auth
def test_register_post_success(client):
    """Test l'inscription d'un nouvel utilisateur"""
    # Envoyer une requête POST pour créer un nouvel utilisateur
    response = client.post('/register', data={
        'pseudo': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'is_admin': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Vérifier que l'utilisateur a été créé dans la base de données
    with client.application.app_context():
        new_user = Utilisateur.query.filter_by(email='newuser@example.com').first()
        assert new_user is not None
        assert new_user.pseudo == 'newuser'
        assert new_user.email == 'newuser@example.com'
        assert new_user.is_admin == False

@pytest.mark.auth
def test_register_post_duplicate_email(client):
    """Test l'inscription avec un email déjà utilisé"""
    # Creer un utilisateur existant
    with client.application.app_context():
        existing_user = Utilisateur(pseudo='existing', email='existing@example.com', is_admin=False)
        existing_user.set_password('password', bcrypt)
        db.session.add(existing_user)
        db.session.commit()
    
    # Essayer de creer un nouvel utilisateur avec le meme email
    response = client.post('/register', data={
        'pseudo': 'newuser',
        'email': 'existing@example.com',  # Email déjà utilisé
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'is_admin': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verifier que l'utilisateur n'a pas été créé (compter les utilisateurs)
    with client.application.app_context():
        user_count = Utilisateur.query.filter_by(email='existing@example.com').count()
        assert user_count == 1  # Seul l'utilisateur existant doit être présent

@pytest.mark.auth
def test_register_post_duplicate_pseudo(client):
    """Test l'inscription avec un pseudo déjà utilisé"""
    # Creer un utilisateur existant
    with client.application.app_context():
        existing_user = Utilisateur(pseudo='existing', email='existing@example.com', is_admin=False)
        existing_user.set_password('password', bcrypt)
        db.session.add(existing_user)
        db.session.commit()
    
    # Essayer de creer un nouvel utilisateur avec le meme pseudo
    response = client.post('/register', data={
        'pseudo': 'existing',  # Pseudo déjà utilisé
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'is_admin': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verifier que l'utilisateur n'a pas été créé (compter les utilisateurs)
    with client.application.app_context():
        user_count = Utilisateur.query.filter_by(pseudo='existing').count()
        assert user_count == 1  # Seul l'utilisateur existant doit être présent

@pytest.mark.auth
def test_login_get(client):
    """Test la route de connexion en GET"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Se connecter' in response.data

@pytest.mark.auth
def test_login_post_success(client):
    """Test la connexion avec des identifiants valides"""
    # Créer un utilisateur pour le test
    with client.application.app_context():
        user = Utilisateur(pseudo='testlogin', email='testlogin@example.com', is_admin=False)
        user.set_password('testpassword', bcrypt)
        db.session.add(user)
        db.session.commit()
    
    # Essayer de se connecter
    response = client.post('/login', data={
        'pseudo': 'testlogin',
        'password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Vérifier que l'utilisateur est bien connecté
    with client.session_transaction() as sess:
        assert '_user_id' in sess

def test_login_post_invalid_credentials(client):
    """Test la connexion avec des identifiants invalides"""
    response = client.post('/login', data={
        'pseudo': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verifier que l'utilisateur n'est pas connecte
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

@pytest.mark.auth
def test_logout(client):
    """Test la déconnexion"""
    # D'abord, connecter un utilisateur
    with client.application.app_context():
        user = Utilisateur(pseudo='testlogout', email='testlogout@example.com', is_admin=False)
        user.set_password('testpassword', bcrypt)
        db.session.add(user)
        db.session.commit()
    
    client.post('/login', data={
        'pseudo': 'testlogout',
        'password': 'testpassword'
    }, follow_redirects=True)
    
    # Vérifier que l'utilisateur est connecté
    with client.session_transaction() as sess:
        assert '_user_id' in sess
    
    # Se déconnecter
    response = client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    # Vérifier que l'utilisateur est bien déconnecté
    with client.session_transaction() as sess:
        assert '_user_id' not in sess


