"""
Test configuration and fixtures for PlanFlan application.

This module contains pytest fixtures and test configuration for the PlanFlan application.
It provides shared test clients, database setup, and test data fixtures.
"""

import pytest
from app import create_app, db
from app.config import TestConfig
from flask_login import login_user
from flask_bcrypt import Bcrypt
from app.models import Utilisateur, Etablissement, Flan, Evaluation


@pytest.fixture(scope="function")
def client():
    """Fixture partagée pour créer un client de test avec un utilisateur connecté"""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False  # Désactiver CSRF pour les tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Créer des données de test avec mot de passe haché
            bcrypt = Bcrypt()
            from app.models import Utilisateur

            user = Utilisateur(pseudo="testuser", email="test@example.com", is_admin=True)
            user.set_password("password", bcrypt)
            db.session.add(user)
            db.session.commit()

            # Vérifier que l'utilisateur a bien été créé
            created_user = Utilisateur.query.filter_by(email="test@example.com").first()
            assert created_user is not None, "L'utilisateur de test n'a pas été créé"
            assert created_user.is_admin == True, "L'utilisateur n'est pas admin"

            # Connexion de l'utilisateur
            login_response = client.post(
                "/login",
                data=dict(pseudo="testuser", password="password"),
                follow_redirects=True,
            )

            # Vérifier que la connexion a réussi
            assert (
                login_response.status_code == 200
            ), f"La connexion a échoué avec le statut {login_response.status_code}"

            # Stocker l'utilisateur créé pour les tests
            app.config["TEST_USER"] = created_user
        yield client

        # Nettoyage après les tests
        with app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="module")
def app():
    """Fixture pour l'application Flask"""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def clean_db():
    """Fixture pour nettoyer la base de données entre les tests"""
    yield
    # Le nettoyage est géré par la fixture client


@pytest.fixture(scope="module")
def setup_minimal_data(app):
    """Crée des données de test minimales pour les tests."""
    with app.app_context():
        bcrypt = Bcrypt()

        # Créer un utilisateur regular
        user = Utilisateur(pseudo="testuser", email="test@example.com", is_admin=False)
        user.set_password("password", bcrypt)

        # Créer un utilisateur admin
        admin = Utilisateur(pseudo="admin", email="admin@example.com", is_admin=True)
        admin.set_password("adminpassword", bcrypt)

        db.session.add_all([user, admin])
        db.session.commit()


@pytest.fixture(scope="module")
def setup_full_data(app):
    """Crée des données de test complètes pour les tests."""
    with app.app_context():
        bcrypt = Bcrypt()

        # Créer un utilisateur regular
        user = Utilisateur(pseudo="testuser", email="test@example.com", is_admin=False)
        user.set_password("password", bcrypt)

        # Créer un utilisateur admin
        admin = Utilisateur(pseudo="admin", email="admin@example.com", is_admin=True)
        admin.set_password("adminpassword", bcrypt)

        db.session.add_all([user, admin])
        db.session.commit()

        # Créer un établissement pour l'utilisateur regular
        etab_user = Etablissement(
            nom="Boulangerie User",
            adresse="1 rue de Test",
            ville="Testville",
            code_postal="69001",
            id_user=user.id_user,
        )

        # Créer un établissement pour l'admin
        etab_admin = Etablissement(
            nom="Boulangerie Admin",
            adresse="2 rue de Test",
            ville="Testville",
            code_postal="69001",
            id_user=admin.id_user,
        )

        db.session.add_all([etab_user, etab_admin])
        db.session.commit()

        # Créer des flans
        flan_user = Flan(nom="Flan User", prix=3.5, id_etab=etab_user.id_etab, id_user=user.id_user, statut="VALIDE")

        flan_admin = Flan(
            nom="Flan Admin",
            prix=4.0,
            id_etab=etab_admin.id_etab,
            id_user=admin.id_user,
            statut="VALIDE",
        )

        db.session.add_all([flan_user, flan_admin])
        db.session.commit()

        # Créer des évaluations
        eval_user = Evaluation(
            visuel=4.0,
            texture=4.5,
            pate=3.5,
            gout=4.0,
            id_flan=flan_user.id_flan,
            id_user=user.id_user,
        )

        eval_admin = Evaluation(
            visuel=5.0,
            texture=5.0,
            pate=5.0,
            gout=5.0,
            id_flan=flan_admin.id_flan,
            id_user=admin.id_user,
        )

        db.session.add_all([eval_user, eval_admin])
        db.session.commit()
