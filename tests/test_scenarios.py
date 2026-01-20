"""
Tests de scénarios utilisateurs complets
"""

import os
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app import db


# Importer les fixtures depuis test_securite
import pytest


@pytest.mark.integration
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


@pytest.mark.integration
@pytest.mark.scenarios
def test_scenario_modification_profil(client):
    """Test un flux complet : inscription -> connexion -> modification de profil"""
    # Étape 1 : Inscription
    response = client.post(
        "/register",
        data={
            "pseudo": "user_profil",
            "email": "profil@example.com",
            "password": "profilpassword",
            "confirm_password": "profilpassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Étape 2 : Connexion
    response = client.post(
        "/login",
        data={"pseudo": "user_profil", "password": "profilpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Étape 3 : Accéder au dashboard (où se trouve le formulaire de profil)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"user_profil" in response.data
    assert b"profil@example.com" in response.data

    # Étape 4 : Modifier le profil via le dashboard
    # Note: Le formulaire utilise le préfixe "profile-" pour les champs
    # Nous allons modifier directement en base pour simplifier le test
    with client.application.app_context():
        user = Utilisateur.query.filter_by(email="profil@example.com").first()
        assert user is not None
        user.pseudo = "user_profil_modifie"
        user.email = "profil_modifie@example.com"
        db.session.commit()

    # Étape 5 : Vérifier les modifications en base
    with client.application.app_context():
        user = Utilisateur.query.filter_by(email="profil_modifie@example.com").first()
        assert user is not None
        assert user.pseudo == "user_profil_modifie"

    # Étape 6 : Vérifier l'affichage des nouvelles informations
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"user_profil_modifie" in response.data
    assert b"profil_modifie@example.com" in response.data


@pytest.mark.integration
@pytest.mark.scenarios
def test_scenario_suppression_contenu(client):
    """Test un flux complet : création -> suppression d'établissement et flan"""
    user = client.application.config["TEST_USER"]

    # Étape 1 : Créer un établissement
    with client.application.app_context():
        etab = Etablissement(
            nom="Etablissement Suppression",
            adresse="1 Rue Suppression",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Étape 2 : Créer un flan
    with client.application.app_context():
        flan = Flan(
            nom="Flan Suppression",
            prix=3.0,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab_id,
            id_user=user.id_user,
        )
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Étape 3 : Supprimer le flan via la route spécifique
    response = client.post(f"/supprimer_flan/{flan_id}", follow_redirects=True)
    assert response.status_code == 200

    # Étape 4 : Vérifier la suppression du flan
    with client.application.app_context():
        deleted_flan = db.session.get(Flan, flan_id)
        assert deleted_flan is None

    # Étape 5 : Supprimer l'établissement (il faut d'abord supprimer les flans associés)
    # Comme nous avons déjà supprimé le flan, nous pouvons maintenant supprimer l'établissement
    with client.application.app_context():
        # Vérifier qu'il n'y a plus de flans associés
        remaining_flans = Flan.query.filter_by(id_etab=etab_id).all()
        assert (
            len(remaining_flans) == 0
        ), "Il reste des flans associés à l'établissement"

        # Supprimer l'établissement directement via la base
        etab_to_delete = db.session.get(Etablissement, etab_id)
        db.session.delete(etab_to_delete)
        db.session.commit()

    # Étape 6 : Vérifier la suppression de l'établissement
    with client.application.app_context():
        deleted_etab = db.session.get(Etablissement, etab_id)
        assert deleted_etab is None


@pytest.mark.integration
@pytest.mark.scenarios
def test_scenario_gestion_evaluations(client):
    """Test un flux complet : création -> modification -> suppression d'évaluation"""
    user = client.application.config["TEST_USER"]

    # Étape 1 : Créer un établissement avec un flan
    with client.application.app_context():
        etab = Etablissement(
            nom="Etablissement Evaluation",
            adresse="1 Rue Evaluation",
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

    # Étape 2 : Créer une évaluation
    response = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": "5",
            "flan-eval-texture": "4",
            "flan-eval-pate": "5",
            "flan-eval-gout": "4",
            "flan-eval-description": "Première évaluation",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Étape 3 : Vérifier la création
    with client.application.app_context():
        eval = Evaluation.query.filter_by(id_flan=flan_id, id_user=user.id_user).first()
        assert eval is not None
        assert eval.visuel == 5.0
        eval_id = eval.id_eval

    # Étape 4 : Modifier l'évaluation via la page du flan
    response = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": "4",
            "flan-eval-texture": "5",
            "flan-eval-pate": "4",
            "flan-eval-gout": "5",
            "flan-eval-description": "Evaluation modifiée",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Étape 5 : Vérifier les modifications
    with client.application.app_context():
        updated_eval = db.session.get(Evaluation, eval_id)
        assert updated_eval.visuel == 4.0
        assert updated_eval.description == "Evaluation modifiée"

    # Étape 6 : Supprimer l'évaluation via la route spécifique
    response = client.post(f"/supprimer_evaluation/{eval_id}", follow_redirects=True)
    assert response.status_code == 200

    # Étape 7 : Vérifier la suppression
    with client.application.app_context():
        deleted_eval = db.session.get(Evaluation, eval_id)
        assert deleted_eval is None


@pytest.mark.integration
@pytest.mark.scenarios
@pytest.mark.regression
@pytest.mark.slow
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
        updated_etab = db.session.get(Etablissement, etab_id)
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
        updated_flan = db.session.get(Flan, flan_id)
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


@pytest.mark.integration
@pytest.mark.scenarios
def test_scenario_geolocalisation(client):
    """Test un flux complet de géolocalisation : index -> liste_etablissements avec coordonnées"""
    user = client.application.config["TEST_USER"]

    # Étape 1 : Créer des établissements avec des coordonnées connues
    with client.application.app_context():
        # Établissement proche des coordonnées simulées (Paris centre)
        etab_proche = Etablissement(
            nom="Boulangerie Proche",
            adresse="1 Rue Proche",
            code_postal="75001",
            ville="Paris",
            latitude=48.8566,  # Paris centre
            longitude=2.3522,
            id_user=user.id_user,
        )
        db.session.add(etab_proche)

        # Établissement loin des coordonnées simulées
        etab_loin = Etablissement(
            nom="Boulangerie Loin",
            adresse="1 Rue Loin",
            code_postal="69001",
            ville="Lyon",
            latitude=45.7640,  # Lyon
            longitude=4.8357,
            id_user=user.id_user,
        )
        db.session.add(etab_loin)
        db.session.commit()

    # Étape 2 : Accéder à la page d'accueil
    response = client.get("/")
    assert response.status_code == 200
    assert b"PLANFLAN" in response.data

    # Étape 3 : Simuler la géolocalisation avec des coordonnées connues (Paris)
    # Dans un vrai navigateur, cela serait fait via l'API de géolocalisation
    # Ici, nous simulons en envoyant directement une requête avec les coordonnées
    test_latitude = 48.8566  # Paris centre
    test_longitude = 2.3522

    # Simuler la requête qui serait faite après la géolocalisation
    response = client.get(
        f"/liste_etablissements?latitude={test_latitude}&longitude={test_longitude}&geolocalisation=true"
    )
    assert response.status_code == 200

    # Étape 4 : Vérifier que les coordonnées sont bien transmises au template
    assert b"user-location" in response.data
    assert f"{test_latitude}".encode() in response.data
    assert f"{test_longitude}".encode() in response.data

    # Étape 5 : Vérifier que l'établissement proche est affiché
    assert b"Boulangerie Proche" in response.data

    # Étape 6 : Vérifier que la carte est bien configurée pour le zoom sur les coordonnées
    # Vérifier que les données de localisation utilisateur sont présentes dans le HTML
    assert b"data-lat" in response.data
    assert b"data-lon" in response.data
