"""
Tests pour la prévention des doublons d'établissements.

Ce module teste les fonctionnalités de détection et de prévention
des doublons d'établissements dans l'application PlanFlan.
"""

import pytest
from app import db, create_app
from app.models import Etablissement, Utilisateur
from app.forms import EtabForm
from flask import url_for


@pytest.fixture
def test_client():
    """Crée un client de test avec configuration TestConfig."""
    app = create_app('app.config.TestConfig')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def etablissement_existant(test_client):
    """Crée un établissement existant pour les tests."""
    etab = Etablissement(
        nom="Boulangerie Test",
        adresse="123 Rue de Test",
        code_postal="75001",
        ville="Paris",
        latitude=48.8566,
        longitude=2.3522,
        type_etab="BOULANGERIE",
        id_user=1
    )
    db.session.add(etab)
    db.session.commit()
    return etab


@pytest.fixture
def utilisateur_test(test_client):
    """Crée un utilisateur de test."""
    user = Utilisateur(
        pseudo="testuser",
        email="test@example.com",
        password="testpassword",
        is_admin=False
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_verifier_etablissement_existant(test_client, etablissement_existant):
    """Test la détection d'un établissement existant via l'API."""
    response = test_client.post('/verifier_etablissement',
                              json={'nom': 'Boulangerie Test'},
                              content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['exists'] is True
    assert data['id_etab'] == etablissement_existant.id_etab
    assert 'url' in data


def test_verifier_etablissement_inexistant(test_client):
    """Test la vérification d'un établissement inexistant."""
    response = test_client.post('/verifier_etablissement',
                              json={'nom': 'Boulangerie Inexistante'},
                              content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['exists'] is False


def test_ajouter_etablissement_doublon(test_client, etablissement_existant):
    """Test l'ajout d'un établissement qui existe déjà (validation serveur)."""
    # Essayer d'ajouter le même établissement
    response = test_client.post('/ajouter_etablissement',
                              data={
                                  'ajout-etab-nom': 'Boulangerie Test',
                                  'ajout-etab-adresse': '123 Rue de Test',
                                  'ajout-etab-code_postal': '75001',
                                  'ajout-etab-ville': 'Paris',
                                  'ajout-etab-latitude': 48.8566,
                                  'ajout-etab-longitude': 2.3522,
                                  'ajout-etab-type_etab': 'BOULANGERIE',
                                  'ajout-etab-google_place_id': 'test_place_id'
                              },
                              follow_redirects=True)
    
    # Should redirect to existing establishment page
    assert response.status_code == 200
    # Should contain the existing establishment ID in the URL or page
    assert b'Boulangerie Test' in response.data


def test_contrainte_unicite_base_donnees(test_client):
    """Test la contrainte d'unicité dans la base de données."""
    # Créer un premier établissement
    etab1 = Etablissement(
        nom="Test Unicité",
        adresse="456 Rue Unique",
        code_postal="75002",
        ville="Paris",
        latitude=48.8566,
        longitude=2.3522,
        type_etab="BOULANGERIE",
        id_user=1
    )
    db.session.add(etab1)
    db.session.commit()
    
    # Essayer de créer un deuxième établissement avec le même nom et adresse
    etab2 = Etablissement(
        nom="Test Unicité",
        adresse="456 Rue Unique",
        code_postal="75002",
        ville="Paris",
        latitude=48.8566,
        longitude=2.3522,
        type_etab="BOULANGERIE",
        id_user=1
    )
    
    db.session.add(etab2)
    
    # Should raise IntegrityError due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy should raise an integrity error
        db.session.commit()
    
    db.session.rollback()


def test_formulaire_etablissement_validation(test_client):
    """Test la validation du formulaire d'établissement."""
    form = EtabForm(prefix="ajout-etab")
    
    # Test avec données valides
    form.nom.data = "Nouvelle Boulangerie"
    form.adresse.data = "789 Nouvelle Rue"
    form.code_postal.data = "75003"
    form.ville.data = "Paris"
    form.latitude.data = 48.8566
    form.longitude.data = 2.3522
    form.type_etab.data = "BOULANGERIE"
    
    assert form.validate() is True


def test_verifier_etablissement_sans_nom(test_client):
    """Test la vérification sans nom d'établissement."""
    response = test_client.post('/verifier_etablissement',
                              json={},
                              content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
