from app import create_app, db
from app.config import TestConfig

import pytest
from flask import get_flashed_messages
from app.models import Etablissement, Evaluation
from app import db
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app.forms import RechercheForm, EtabForm, NewFlanForm, EvalForm, UpdateProfileForm, DeleteForm, ValidateForm
from flask_login import current_user, login_user
from flask import session, template_rendered, request
from flask import get_flashed_messages

from flask_bcrypt import Bcrypt


def test_geoloc_route(client):
    """Test de la route /geoloc pour la géolocalisation"""
    response = client.post('/geoloc', json={
        'latitude': 45.764043,
        'longitude': 4.835659
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'latitude' in data
    assert 'longitude' in data

def test_etablissements_proches_route(client):
    """Test de la route /etablissements_proches"""
    user = client.application.config['TEST_USER']

    with client.application.app_context():
        # Créer un établissement de référence
        etab_ref = Etablissement(
            nom='Etablissement Reference',
            adresse='1 rue de la République',
            code_postal='69001',
            ville='Lyon',
            latitude=45.764043,
            longitude=4.835659,
            id_user=user.id_user
        )
        db.session.add(etab_ref)

        # Créer des établissements proches
        for i in range(3):
            etab = Etablissement(
                nom=f'Etablissement Proche {i}',
                adresse=f'{i+1} rue de la République',
                code_postal='69001',
                ville='Lyon',
                latitude=45.764043 + (i * 0.001),
                longitude=4.835659 + (i * 0.001),
                id_user=user.id_user
            )
            db.session.add(etab)

        db.session.commit()

    # Tester la route
    response = client.post('/etablissements_proches', json={
        'latitude': 45.764043,
        'longitude': 4.835659,
        'distance_max': 1  # 1 km
    })
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0, "Aucun établissement proche trouvé"

def test_extraire_infos_adresse_route(client):
    """Test de la route /extraire_infos_adresse"""
    response = client.post('/extraire_infos_adresse', json={
        'adresse': '1 rue de la République, 69001 Lyon'
    })
    assert response.status_code == 200
    data = response.get_json()
    # La route retourne 'adresse_nettoyee' au lieu de 'adresse'
    assert 'adresse_nettoyee' in data
    assert 'code_postal' in data
    assert 'ville' in data

def test_proposer_etablissement_get(client):
    """Test de la route /proposer_etablissement en GET"""
    response = client.get('/proposer_etablissement')
    assert response.status_code == 200
    # Vérifier que la page contient un formulaire (plus générique)
    assert b'form' in response.data
    assert b'input' in response.data

def test_proposer_etablissement_post(client):
    """Test de la route /proposer_etablissement en POST - cette route ne crée pas d'établissement, elle affiche juste le formulaire"""
    user = client.application.config['TEST_USER']

    # Cette route ne fait que rendre un template, elle ne crée pas d'établissement
    # Nous testons juste qu'elle répond correctement
    response = client.post('/proposer_etablissement', data={
        'ajout-etab-nom': 'Nouvel Etablissement Test',
        'ajout-etab-adresse': '10 rue de Test',
        'ajout-etab-code_postal': '69001',
        'ajout-etab-ville': 'Lyon',
        'ajout-etab-type_etab': 'BOULANGERIE',
        'ajout-etab-description': 'Description de test',
        'ajout-etab-telephone': '0123456789',
        'ajout-etab-site_web': 'http://test.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Vérifier que la page contient bien un formulaire
    assert b'form' in response.data
    # La route /proposer_etablissement ne crée pas d'établissement, elle affiche juste le formulaire
    # Donc aucun message de succès n'est attendu

def test_verifier_etablissement_route(client):
    """Test de la route /verifier_etablissement"""
    user = client.application.config['TEST_USER']

    with client.application.app_context():
        # Créer un établissement non validé
        etab = Etablissement(
            nom='Etablissement à vérifier',
            adresse='1 rue de Test',
            code_postal='69001',
            ville='Lyon',
            id_user=user.id_user,
            statut='EN_ATTENTE'
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Tester la vérification - la route attend un JSON avec le nom, pas un ID
    response = client.post('/verifier_etablissement', json={
        'nom': 'Etablissement à vérifier'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['exists'] == True
    assert data['id_etab'] == etab_id

def test_ajouter_etablissement_route(client):
    """Test de la route /ajouter_etablissement"""
    user = client.application.config['TEST_USER']

    # Compter les établissements avant
    with client.application.app_context():
        count_before = Etablissement.query.filter_by(id_user=user.id_user).count()

    # Envoyer le formulaire d'ajout avec le bon préfixe
    response = client.post('/ajouter_etablissement', data={
        'ajout-etab-nom': 'Etablissement Ajouté',
        'ajout-etab-adresse': '20 rue de Test',
        'ajout-etab-code_postal': '69001',
        'ajout-etab-ville': 'Lyon',
        'ajout-etab-type_etab': 'BOULANGERIE',
        'ajout-etab-description': 'Description ajoutée',
        'ajout-etab-telephone': '0123456789',
        'ajout-etab-site_web': 'http://ajout.com'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Vérifier que l'établissement a été ajouté
    with client.application.app_context():
        count_after = Etablissement.query.filter_by(id_user=user.id_user).count()
        assert count_after == count_before + 1, "L'établissement n'a pas été ajouté"

def test_modifier_etablissement_route(client):
    """Test de la route /modifier_etablissement"""
    user = client.application.config['TEST_USER']

    with client.application.app_context():
        # Créer un établissement à modifier
        etab = Etablissement(
            nom='Etablissement Original',
            adresse='1 rue Originale',
            code_postal='69001',
            ville='Lyon',
            latitude=45.764043,
            longitude=4.835659,
            type_etab='BOULANGERIE',
            id_user=user.id_user
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Envoyer le formulaire de modification avec le bon préfixe
    response = client.post(f'/modifier_etablissement/{etab_id}', data={
        'edit-etab-nom': 'Etablissement Modifié',
        'edit-etab-adresse': '2 rue Modifiée',
        'edit-etab-code_postal': '69001',
        'edit-etab-ville': 'Lyon',
        'edit-etab-type_etab': 'BOULANGERIE',
        'edit-etab-description': 'Description modifiée',
        'edit-etab-label': 'Oui',
        'edit-etab-visite': 'Oui',
        'edit-etab-latitude': '45.764043',
        'edit-etab-longitude': '4.835659'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Vérifier que l'établissement a été modifié
    with client.application.app_context():
        updated_etab = Etablissement.query.get(etab_id)
        assert updated_etab.nom == 'Etablissement Modifié', "Le nom n'a pas été modifié"
        assert updated_etab.adresse == '2 rue Modifiée', "L'adresse n'a pas été modifiée"


def test_valider_etablissement_route(client):
    """Test de la route /valider_etablissement (admin seulement)"""
    user = client.application.config['TEST_USER']
    assert user.is_admin, "L'utilisateur doit être admin pour ce test"

    with client.application.app_context():
        # Créer un établissement non validé
        etab = Etablissement(
            nom='Etablissement à valider',
            adresse='1 rue de Validation',
            code_postal='69001',
            ville='Lyon',
            id_user=user.id_user,
            statut='EN_ATTENTE'
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Envoyer la requête de validation
    response = client.post(f'/valider_etablissement/{etab_id}')
    assert response.status_code == 302  # Redirection

    # Vérifier que l'établissement a été validé
    with client.application.app_context():
        updated_etab = Etablissement.query.get(etab_id)
        assert updated_etab.statut.value == 'VALIDE', f"L'établissement n'a pas été validé. Statut: {updated_etab.statut.value}"

def test_supprimer_etablissement_route(client):
    """Test de la route /supprimer_etablissement"""
    user = client.application.config['TEST_USER']

    with client.application.app_context():
        # Créer un établissement à supprimer
        etab = Etablissement(
            nom='Etablissement à supprimer',
            adresse='1 rue de Suppression',
            code_postal='69001',
            ville='Lyon',
            id_user=user.id_user
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Envoyer la requête de suppression
    response = client.post(f'/supprimer_etablissement/{etab_id}')
    assert response.status_code == 302  # Redirection

    # Vérifier que l'établissement a été supprimé
    with client.application.app_context():
        deleted_etab = Etablissement.query.get(etab_id)
        assert deleted_etab is None, "L'établissement n'a pas été supprimé"
