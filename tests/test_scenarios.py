"""
Tests de scénarios utilisateurs complets
"""

from app.models import Etablissement, Flan, Evaluation
from app import db


# Importer les fixtures depuis test_securite
import pytest


@pytest.mark.scenarios
def test_scenario_inscription_connexion_creation_flan(client):
    """Test un flux complet : inscription -> connexion -> création de flan"""
    # Étape 1 : Inscription d'un nouvel utilisateur
    response = client.post(
        "/register",
        data={
            "pseudo": "scenario_user",
            "email": "scenario@example.com",
            "password": "scenariopassword",
            "confirm_password": "scenariopassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Étape 2 : Connexion
    response = client.post(
        "/login",
        data={"pseudo": "scenario_user", "password": "scenariopassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Vérifier que l'utilisateur est connecté
    with client.session_transaction() as sess:
        assert "_user_id" in sess

    # Étape 3 : Créer un établissement
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        etab = Etablissement(
            nom="Etablissement Scenario",
            adresse="1 Rue Scenario",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Étape 4 : Créer un flan pour cet établissement
    response = client.post(
        f"/etablissement/{etab_id}/proposer_flan",
        data={
            "ajout-flan-nom": "Flan Scenario",
            "ajout-flan-prix": 3.5,
            "ajout-flan-description": "Description du flan scenario",
            "ajout-flan-type_pate": "BRISEE",
            "ajout-flan-type_saveur": "VANILLE",
            "ajout-flan-type_texture": "CREMEUSE",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Vérifier que le flan a été créé
    with client.application.app_context():
        flan = Flan.query.filter_by(nom="Flan Scenario").first()
        assert flan is not None
        assert flan.prix == 3.5
        assert flan.id_etab == etab_id


@pytest.mark.scenarios
def test_scenario_recherche_et_evaluation(client):
    """Test un flux complet : recherche -> consultation -> évaluation"""
    user = client.application.config["TEST_USER"]

    # Étape 1 : Créer un établissement avec un flan
    with client.application.app_context():
        etab = Etablissement(
            nom="Etablissement Evaluation",
            adresse="2 Rue Evaluation",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(
            nom="Flan Evaluation",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="FRUITS",
            type_texture="GELATINEUSE",
            id_etab=etab.id_etab,
            id_user=user.id_user,
        )
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Étape 2 : Rechercher l'établissement
    response = client.get("/liste_etablissements?recherche_simple=Evaluation")
    assert response.status_code == 200
    assert b"Etablissement Evaluation" in response.data

    # Étape 3 : Consulter le flan
    response = client.get(f"/flan/{flan_id}")
    assert response.status_code == 200
    assert b"Flan Evaluation" in response.data

    # Étape 4 : Évaluer le flan
    response = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": 5,
            "flan-eval-texture": 4,
            "flan-eval-pate": 5,
            "flan-eval-gout": 4,
            "flan-eval-description": "Excellent flan!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Vérifier que l'évaluation a été créée
    with client.application.app_context():
        eval = Evaluation.query.filter_by(id_flan=flan_id, id_user=user.id_user).first()
        assert eval is not None
        assert eval.visuel == 5.0
        assert eval.gout == 4.0
        assert eval.description == "Excellent flan!"


@pytest.mark.scenarios
def test_scenario_administration_complete(client):
    """Test un flux complet d'administration : création utilisateur -> validation contenu"""
    # Ce test nécessite un utilisateur admin
    user = client.application.config["TEST_USER"]
    assert user.is_admin, "L'utilisateur doit être admin pour ce test"

    # Étape 1 : Créer un nouvel utilisateur (par admin)
    with client.application.app_context():
        from app.models import Utilisateur
        from app import bcrypt

        new_user = Utilisateur(
            pseudo="user_cree_par_admin", email="useradmin@example.com", is_admin=False
        )
        new_user.set_password("userpassword", bcrypt)
        db.session.add(new_user)
        db.session.commit()

    # Étape 2 : Créer un établissement non validé
    with client.application.app_context():
        # Utiliser l'ID de l'utilisateur admin directement
        admin_user = Utilisateur.query.filter_by(email="test@example.com").first()
        etab = Etablissement(
            nom="Etablissement Admin",
            adresse="3 Rue Admin",
            code_postal="69001",
            ville="Lyon",
            id_user=admin_user.id_user,
            statut="EN_ATTENTE",
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Étape 3 : Valider l'établissement
    response = client.post(f"/valider_etablissement/{etab_id}")
    assert response.status_code == 302  # Redirection

    # Vérifier que l'établissement a été validé
    with client.application.app_context():
        updated_etab = Etablissement.query.get(etab_id)
        assert updated_etab.statut.value == "VALIDE"

    # Étape 4 : Créer un flan non validé
    with client.application.app_context():
        # Utiliser l'ID de l'utilisateur admin directement
        admin_user = Utilisateur.query.filter_by(email="test@example.com").first()
        flan = Flan(
            nom="Flan Admin",
            prix=3.0,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab_id,
            id_user=admin_user.id_user,
            statut="EN_ATTENTE",
        )
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Étape 5 : Valider le flan
    response = client.post(f"/valider_flan/{flan_id}")
    assert response.status_code == 302  # Redirection

    # Vérifier que le flan a été validé
    with client.application.app_context():
        updated_flan = Flan.query.get(flan_id)
        assert updated_flan.statut.value == "VALIDE"


@pytest.mark.scenarios
def test_scenario_recherche_avancee(client):
    """Test un scénario de recherche avancée avec multiples filtres"""
    user = client.application.config["TEST_USER"]

    # Créer plusieurs établissements avec différents attributs
    with client.application.app_context():
        # Établissement 1 : Boulangerie visitée
        etab1 = Etablissement(
            nom="Boulangerie Visitee",
            adresse="1 Rue Boulangerie",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
            visite=True,
            label=False,
        )
        db.session.add(etab1)
        db.session.commit()

        flan1 = Flan(
            nom="Flan Boulangerie",
            prix=2.0,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=user.id_user,
        )
        db.session.add(flan1)

        # Établissement 2 : Pâtisserie labellisée
        etab2 = Etablissement(
            nom="Patisserie Labellisee",
            adresse="2 Rue Patisserie",
            code_postal="69002",
            ville="Lyon",
            id_user=user.id_user,
            visite=False,
            label=True,
        )
        db.session.add(etab2)
        db.session.commit()

        flan2 = Flan(
            nom="Flan Patisserie",
            prix=4.5,
            type_pate="SABLEE",
            type_saveur="FRUITS",
            type_texture="GELATINEUSE",
            id_etab=etab2.id_etab,
            id_user=user.id_user,
        )
        db.session.add(flan2)
        db.session.commit()

    # Test 1 : Filtrer par visite
    response = client.get("/liste_etablissements?visite=oui")
    assert response.status_code == 200
    assert b"Boulangerie Visitee" in response.data
    assert b"Patisserie Labellisee" not in response.data

    # Test 2 : Filtrer par labellisé
    response = client.get("/liste_etablissements?labellise=oui")
    assert response.status_code == 200
    assert b"Patisserie Labellisee" in response.data
    assert b"Boulangerie Visitee" not in response.data

    # Test 3 : Filtrer par type de pâte
    response = client.get("/liste_etablissements?type_pate=SABLEE")
    assert response.status_code == 200
    assert b"Patisserie Labellisee" in response.data
    assert b"Boulangerie Visitee" not in response.data

    # Test 4 : Filtrer par gamme de prix (moins de 2.5€)
    response = client.get("/liste_etablissements?prix=0")
    assert response.status_code == 200
    assert b"Boulangerie Visitee" in response.data
    assert b"Patisserie Labellisee" not in response.data
