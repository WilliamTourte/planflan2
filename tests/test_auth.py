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
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Creer un compte" in response.data


@pytest.mark.auth
@pytest.mark.parametrize(
    "test_name,user_data,setup_existing,expected_success,check_field,check_value",
    [
        # Test inscription réussie
        (
            "success",
            {
                "pseudo": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword",
                "confirm_password": "newpassword",
                "is_admin": False,
            },
            None,
            True,
            "email",
            "newuser@example.com",
        ),
        # Test email déjà utilisé
        (
            "duplicate_email",
            {
                "pseudo": "newuser",
                "email": "existing@example.com",  # Email déjà utilisé
                "password": "newpassword",
                "confirm_password": "newpassword",
                "is_admin": False,
            },
            {"pseudo": "existing", "email": "existing@example.com"},
            False,
            "email",
            "existing@example.com",
        ),
        # Test pseudo déjà utilisé
        (
            "duplicate_pseudo",
            {
                "pseudo": "existing",  # Pseudo déjà utilisé
                "email": "newuser@example.com",
                "password": "newpassword",
                "confirm_password": "newpassword",
                "is_admin": False,
            },
            {"pseudo": "existing", "email": "existing@example.com"},
            False,
            "pseudo",
            "existing",
        ),
    ],
)
def test_register_post_parametrize(
    client,
    test_name,
    user_data,
    setup_existing,
    expected_success,
    check_field,
    check_value,
):
    """Test l'inscription avec différents scénarios (paramétrisé)"""
    # Créer un utilisateur existant si nécessaire
    if setup_existing:
        with client.application.app_context():
            existing_user = Utilisateur(
                pseudo=setup_existing["pseudo"],
                email=setup_existing["email"],
                is_admin=False,
            )
            existing_user.set_password("password", bcrypt)
            db.session.add(existing_user)
            db.session.commit()

    # Envoyer une requête POST pour créer un nouvel utilisateur
    response = client.post(
        "/register",
        data=user_data,
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier le résultat attendu
    with client.application.app_context():
        if expected_success:
            # Pour les inscriptions réussies, vérifier que l'utilisateur a été créé
            new_user = Utilisateur.query.filter_by(email=user_data["email"]).first()
            assert new_user is not None
            assert new_user.pseudo == user_data["pseudo"]
            assert new_user.email == user_data["email"]
            assert new_user.is_admin == user_data["is_admin"]

            # Vérifier que l'utilisateur est connecté
            with client.session_transaction() as sess:
                assert "_user_id" in sess
                assert sess["_user_id"] == str(new_user.id_user)
        else:
            # Pour les échecs, vérifier que l'utilisateur n'a pas été créé
            user_count = Utilisateur.query.filter_by(**{check_field: check_value}).count()
            assert user_count == 1  # Seul l'utilisateur existant doit être présent


@pytest.mark.auth
def test_login_get(client):
    """Test la route de connexion en GET"""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Se connecter" in response.data


@pytest.mark.auth
@pytest.mark.parametrize(
    "test_name,setup_user,login_data,expected_success",
    [
        # Test connexion réussie
        (
            "success",
            {
                "pseudo": "testlogin",
                "email": "testlogin@example.com",
                "password": "testpassword",
            },
            {"pseudo": "testlogin", "password": "testpassword"},
            True,
        ),
        # Test identifiants invalides
        (
            "invalid_credentials",
            None,
            {"pseudo": "nonexistent", "password": "wrongpassword"},
            False,
        ),
    ],
)
def test_login_post_parametrize(client, test_name, setup_user, login_data, expected_success):
    """Test la connexion avec différents scénarios (paramétrisé)"""
    # Créer un utilisateur pour le test si nécessaire
    if setup_user:
        with client.application.app_context():
            user = Utilisateur(
                pseudo=setup_user["pseudo"],
                email=setup_user["email"],
                is_admin=False,
            )
            user.set_password(setup_user["password"], bcrypt)
            db.session.add(user)
            db.session.commit()

    # Essayer de se connecter
    response = client.post(
        "/login",
        data=login_data,
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier le résultat de la connexion
    with client.session_transaction() as sess:
        if expected_success:
            assert "_user_id" in sess
        else:
            assert "user_id" not in sess


@pytest.mark.auth
def test_logout(client):
    """Test la déconnexion"""
    # D'abord, connecter un utilisateur
    with client.application.app_context():
        user = Utilisateur(pseudo="testlogout", email="testlogout@example.com", is_admin=False)
        user.set_password("testpassword", bcrypt)
        db.session.add(user)
        db.session.commit()

    client.post(
        "/login",
        data={"pseudo": "testlogout", "password": "testpassword"},
        follow_redirects=True,
    )

    # Vérifier que l'utilisateur est connecté
    with client.session_transaction() as sess:
        assert "_user_id" in sess

    # Se déconnecter
    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    # Vérifier que l'utilisateur est bien déconnecté
    with client.session_transaction() as sess:
        assert "_user_id" not in sess
