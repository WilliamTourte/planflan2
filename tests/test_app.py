from app import create_app, db
from app.config import TestConfig
import pytest

from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app.forms import RechercheForm, EtabForm, NewFlanForm, EvalForm, UpdateProfileForm, DeleteForm, ValidateForm
from flask_login import current_user
from flask import session, template_rendered, request

@pytest.fixture
def client():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Créer des données de test
            user = Utilisateur(pseudo='testuser', email='test@example.com', password='password', is_admin=True)
            db.session.add(user)
            db.session.commit()
            # Connexion de l'utilisateur
            client.post('/login', data=dict(
                email='test@example.com',
                password='password'
            ), follow_redirects=True)
        yield client


def test_example(client):
    response = client.get('/')
    assert response.status_code == 200

def test_liste_etab(client):
    response = client.get('/liste_etablissements')
    assert response.status_code == 200





def test_rechercher(client):
    response = client.get('/rechercher')
    assert response.status_code == 200
    assert b'Rechercher' in response.data



def test_afficher_etablissement_unique(client):
    # Créer un établissement de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville', adresse='Test Adresse', code_postal='69001', id_user=1)
    db.session.add(etab)
    db.session.commit()
    response = client.get(f'/etablissement/{etab.id_etab}')
    assert response.status_code == 200


def test_afficher_flan_unique(client):
    # Créer un établissement et un flan de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville', adresse='Test Adresse', code_postal='69001', id_user="1", id_etab="1")
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    db.session.commit()
    response = client.get(f'/flan/{flan.id_flan}')
    assert response.status_code == 200
    assert b'Test Flan' in response.data

from flask import get_flashed_messages

from flask_bcrypt import Bcrypt
def test_proposer_flan(client):
    # Récupérer l'utilisateur déjà créé et connecté dans la fixture
    with client.application.app_context():
        user = Utilisateur.query.filter_by(email='test@example.com').first()
        assert user is not None, "L'utilisateur de test n'existe pas"

     # Simuler la connexion avec login_user
    login_user(user)

    # Créer un établissement de test lié à cet utilisateur
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville', adresse='Test Adresse', code_postal='69001', id_user=user.id_user)
    db.session.add(etab)
    db.session.commit()

    # Envoyer la requête
    response = client.post(
        f'/etablissement/{etab.id_etab}/proposer_flan',
        data=dict(nom='Nouveau Flan', prix=2.5),
        follow_redirects=True
    )

    # Vérifier le statut HTTP
    assert response.status_code == 200

    # Récupérer et afficher les messages flash
    flashed_messages = get_flashed_messages(with_categories=True)
    print("Messages flash récupérés :", flashed_messages)

    # Vérifier qu'il y a au moins un message flash
    assert len(flashed_messages) > 0, "Aucun message flash trouvé"

    # Vérifier qu'au moins un message est de catégorie 'success'
    categories = [category for category, _ in flashed_messages]
    print("Catégories des messages :", categories)
    assert 'success' in categories, f"Catégorie 'success' non trouvée dans {categories}"


def test_valider_flan(client):
    # Créer un établissement et un flan de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    db.session.commit()
    response = client.post(f'/valider_flan/{flan.id_flan}')
    assert response.status_code == 302  # Redirection
    assert flan.statut == 'valide'

def test_modifier_flan(client):
    # Créer un établissement et un flan de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    db.session.commit()
    response = client.post(f'/modifier_flan/{flan.id_flan}', data=dict(
        nom='Nouveau Nom',
        prix=3.0
    ), follow_redirects=True)
    assert response.status_code == 200
    assert 'Le flan a été mis à jour avec succès' in response.get_data(as_text=True)

def test_supprimer_flan(client):
    # Créer un établissement et un flan de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    db.session.commit()
    response = client.post(f'/supprimer_flan/{flan.id_flan}')
    assert response.status_code == 302  # Redirection
    assert Flan.query.get(flan.id_flan) is None

def test_evaluer_flan(client):
    # Créer un établissement et un flan de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    db.session.commit()
    response = client.post(f'/flan/{flan.id_flan}/evaluer', data=dict(
        visuel=5,
        texture=5,
        pate=5,
        gout=5,
        description='Test Description'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert 'Votre évaluation a été mise à jour avec succès' in response.get_data(as_text=True)

def test_afficher_evaluation_unique(client):
    # Créer un établissement, un flan et une évaluation de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    eval = Evaluation(visuel=5, texture=5, pate=5, gout=5, description='Test Description', id_flan=flan.id_flan, id_user=1)
    db.session.add(eval)
    db.session.commit()
    response = client.get(f'/evaluation/{eval.id_eval}')
    assert response.status_code == 200
    assert 'Test Description' in response.get_data(as_text=True)

def test_valider_evaluation(client):
    # Créer un établissement, un flan et une évaluation de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    eval = Evaluation(visuel=5, texture=5, pate=5, gout=5, description='Test Description', id_flan=flan.id_flan, id_user=1)
    db.session.add(eval)
    db.session.commit()
    response = client.post(f'/valider_evaluation/{eval.id_eval}')
    assert response.status_code == 302  # Redirection
    assert eval.statut == 'VALIDE'

def test_supprimer_evaluation(client):
    # Créer un établissement, un flan et une évaluation de test
    etab = Etablissement(nom='Test Etablissement', ville='Test Ville')
    db.session.add(etab)
    flan = Flan(nom='Test Flan', prix=2.5, id_etab=etab.id_etab)
    db.session.add(flan)
    eval = Evaluation(visuel=5, texture=5, pate=5, gout=5, description='Test Description', id_flan=flan.id_flan, id_user=1)
    db.session.add(eval)
    db.session.commit()
    response = client.post(f'/supprimer_evaluation/{eval.id_eval}')
    assert response.status_code == 302  # Redirection
    assert Evaluation.query.get(eval.id_eval) is None