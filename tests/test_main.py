"""
Main application tests for PlanFlan.

This module contains comprehensive tests for the main application routes and functionality,
including user authentication, establishment management, flan operations, and evaluations.
"""

from app import db
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app.forms import (
    RechercheForm,
    EtabForm,
    NewFlanForm,
    EvalForm,
    UpdateProfileForm,
    DeleteForm,
    ValidateForm,
)
from flask_login import current_user
from flask import get_flashed_messages
import pytest

# Importer les fixtures depuis test_securite


@pytest.mark.main
@pytest.mark.smoke
@pytest.mark.parametrize(
    "route,expected_status,expected_content",
    [
        ("/", 200, None),
        ("/liste_etablissements", 200, None),
        ("/rechercher", 200, b"Rechercher"),
        ("/dashboard", 200, b"Tableau de bord"),
    ],
)
def test_route_status(client, route, expected_status, expected_content):
    """Test multiple routes with parameterized inputs"""
    response = client.get(route)
    assert response.status_code == expected_status

    if expected_content is not None:
        assert expected_content in response.data


def test_afficher_etablissement_unique(client):
    """Test displaying a single establishment page."""
    # Créer un établissement de test
    etab = Etablissement(
        nom="Test Etablissement",
        ville="Test Ville",
        adresse="Test Adresse",
        code_postal="69001",
        id_user=1,
    )
    db.session.add(etab)
    db.session.commit()
    response = client.get(f"/etablissement/{etab.id_etab}")
    assert response.status_code == 200


def test_afficher_flan_unique(client):
    """Test displaying a single flan page."""
    # Créer un établissement et un flan de test
    etab = Etablissement(
        nom="Test Etablissement",
        ville="Test Ville",
        adresse="Test Adresse",
        code_postal="69001",
        id_user="1",
        id_etab="1",
    )
    db.session.add(etab)
    flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, statut="VALIDE")
    db.session.add(flan)
    db.session.commit()
    response = client.get(f"/flan/{flan.id_flan}")
    assert response.status_code == 200
    assert b"Test Flan" in response.data


def test_proposer_flan(client):
    """Test proposing a new flan."""
    # Récupérer l'utilisateur créé dans la fixture (déjà connecté via la fixture)
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement de test lié à cet utilisateur
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            ville="Test Ville",
            adresse="Test Adresse",
            code_postal="69001",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Compter le nombre de flans avant la création
    with client.application.app_context():
        flans_before = Flan.query.filter_by(id_etab=etab_id).count()

    # Envoyer la requête - l'utilisateur est déjà connecté via la fixture
    # Utiliser les données du formulaire comme attendues par la route
    response = client.post(
        f"/etablissement/{etab_id}/proposer_flan",
        data={
            "ajout-flan-nom": "Nouveau Flan",
            "ajout-flan-prix": 2.5,
            "ajout-flan-description": "Description du flan",
            "ajout-flan-type_pate": "BRISEE",
            "ajout-flan-type_saveur": "VANILLE",
            "ajout-flan-type_texture": "CREMEUSE",
        },
        follow_redirects=True,
    )

    # Vérifier le statut HTTP (200 pour la page ou 302 pour redirection)
    assert response.status_code in [200, 302]

    # Vérifier que le flan a été créé dans la base de données
    with client.application.app_context():
        flans_after = Flan.query.filter_by(id_etab=etab_id).count()
        assert (
            flans_after == flans_before + 1
        ), f"Le flan n'a pas été créé. Avant: {flans_before}, Après: {flans_after}"

        # Vérifier que le flan a les bonnes propriétés
        nouveau_flan = Flan.query.filter_by(nom="Nouveau Flan").first()
        assert (
            nouveau_flan is not None
        ), "Le nouveau flan n'a pas été trouvé dans la base de données"
        assert nouveau_flan.prix == 2.5, f"Le prix du flan est incorrect: {nouveau_flan.prix}"
        assert nouveau_flan.id_user == user.id_user, "L'ID de l'utilisateur n'est pas correct"

    # Récupérer et afficher les messages flash
    flashed_messages = get_flashed_messages(with_categories=True)
    print("Messages flash récupérés :", flashed_messages)

    # Vérifier qu'il y a au moins un message flash de succès
    assert len(flashed_messages) > 0, "Aucun message flash trouvé"

    # Vérifier que le message contient une indication de succès
    messages = [message for category, message in flashed_messages]
    categories = [category for category, message in flashed_messages]
    print("Messages :", messages)
    print("Catégories :", categories)

    success_condition = any("succès" in message.lower() for message in messages)
    assert success_condition, f"Aucun message de succès trouvé. Messages: {messages}"


@pytest.mark.main
@pytest.mark.main
def test_modifier_flan(client):
    """Test modifying a flan."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Envoyer la requête de modification avec les bons noms de champs
    response = client.post(
        f"/modifier_flan/{flan_id}",
        data={
            "edit-flan-nom": "Nouveau Nom",
            "edit-flan-prix": 3.0,
            "edit-flan-description": "Nouvelle description",
            "edit-flan-type_pate": "BRISEE",
            "edit-flan-type_saveur": "VANILLE",
            "edit-flan-type_texture": "CREMEUSE",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier que le flan a été mis à jour dans la base de données
    with client.application.app_context():
        updated_flan = db.session.get(Flan, flan_id)
        assert (
            updated_flan.nom == "Nouveau Nom"
        ), f"Le nom du flan n'a pas été mis à jour: {updated_flan.nom}"
        assert (
            updated_flan.prix == 3.0
        ), f"Le prix du flan n'a pas été mis à jour: {updated_flan.prix}"

    # Vérifier le message de succès
    flashed_messages = get_flashed_messages(with_categories=True)
    messages = [message for category, message in flashed_messages]
    assert any(
        "mis à jour" in message.lower() for message in messages
    ), f"Aucun message de mise à jour trouvé: {messages}"


@pytest.mark.main
def test_supprimer_flan(client):
    """Test deleting a flan."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Envoyer la requête de suppression
    response = client.post(f"/supprimer_flan/{flan_id}")
    assert response.status_code == 302  # Redirection

    # Vérifier que le flan a été supprimé de la base de données
    with client.application.app_context():
        deleted_flan = db.session.get(Flan, flan_id)
        assert deleted_flan is None, "Le flan n'a pas été supprimé de la base de données"


@pytest.mark.main
def test_evaluer_flan(client):
    """Test evaluating a flan."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Envoyer la requête d'évaluation avec les bons noms de champs
    # Le formulaire utilise un prefix "flan-eval" donc les noms des champs sont préfixés
    # Format uniforme avec .0 pour les entiers
    response = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": 5.0,
            "flan-eval-texture": 5.0,
            "flan-eval-pate": 5.0,
            "flan-eval-gout": 5.0,
            "flan-eval-description": "Test Description",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier que l'évaluation a été créée dans la base de données
    with client.application.app_context():
        evaluations = Evaluation.query.filter_by(id_flan=flan_id, id_user=user.id_user).all()
        assert len(evaluations) > 0, "Aucune évaluation n'a été créée"

        # Vérifier les valeurs de l'évaluation
        eval = evaluations[0]
        assert eval.visuel == 5, f"La note visuel est incorrecte: {eval.visuel}"
        assert eval.texture == 5, f"La note texture est incorrecte: {eval.texture}"
        assert eval.pate == 5, f"La note pate est incorrecte: {eval.pate}"
        assert eval.gout == 5, f"La note gout est incorrecte: {eval.gout}"
        assert (
            eval.description == "Test Description"
        ), f"La description est incorrecte: {eval.description}"

    # Vérifier le message de succès
    flashed_messages = get_flashed_messages(with_categories=True)
    messages = [message for category, message in flashed_messages]
    assert any(
        "évaluation" in message.lower() and "succès" in message.lower() for message in messages
    ), f"Aucun message de succès trouvé: {messages}"


def test_evaluer_flan_duplicate_prevention(client):
    """Test that a user cannot create a second evaluation for the same flan."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Créer une première évaluation
    # Le formulaire utilise un prefix "flan-eval" donc les noms des champs sont préfixés
    # Format uniforme avec .0 pour les entiers
    response1 = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": 5.0,
            "flan-eval-texture": 5.0,
            "flan-eval-pate": 5.0,
            "flan-eval-gout": 5.0,
            "flan-eval-description": "First Evaluation",
        },
        follow_redirects=True,
    )
    assert response1.status_code == 200

    # Vérifier que la première évaluation a été créée
    with client.application.app_context():
        evaluations = Evaluation.query.filter_by(id_flan=flan_id, id_user=user.id_user).all()
        assert len(evaluations) == 1, "Une seule évaluation devrait exister"
        first_eval_id = evaluations[0].id_eval

    # Tenter de créer une deuxième évaluation
    response2 = client.post(
        f"/flan/{flan_id}/evaluer",
        data={
            "flan-eval-visuel": 4,
            "flan-eval-texture": 4,
            "flan-eval-pate": 4,
            "flan-eval-gout": 4,
            "flan-eval-description": "Second Evaluation",
        },
        follow_redirects=True,
    )
    assert response2.status_code == 200

    # Vérifier que la deuxième évaluation a été rejetée
    with client.application.app_context():
        evaluations = Evaluation.query.filter_by(id_flan=flan_id, id_user=user.id_user).all()
        assert len(evaluations) == 1, "Une seule évaluation devrait exister (création bloquée)"

        # Vérifier que l'évaluation n'a pas été modifiée par la tentative
        eval_obj = evaluations[0]
        assert (
            eval_obj.description == "First Evaluation"
        ), "La première évaluation ne devrait pas être modifiée par le rejet de la deuxième"


def test_afficher_evaluation_unique(client):
    """Test displaying a single evaluation."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement, un flan et une évaluation de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()

        eval = Evaluation(
            visuel=5,
            texture=5,
            pate=5,
            gout=5,
            description="Test Description",
            id_flan=flan.id_flan,
            id_user=user.id_user,
        )
        db.session.add(eval)
        db.session.commit()
        eval_id = eval.id_eval

    # Accéder à la page de l'évaluation
    response = client.get(f"/evaluation/{eval_id}")
    assert response.status_code == 200
    # La description n'est plus affichée sur la page
    # Vérifier que les critères d'évaluation sont affichés
    assert b"Visuel" in response.data or b"visuel" in response.data.lower()


def test_supprimer_evaluation(client):
    """Test deleting an evaluation."""
    # Récupérer l'utilisateur créé dans la fixture
    user = client.application.config["TEST_USER"]
    assert user is not None, "L'utilisateur de test n'existe pas"

    # Créer un établissement, un flan et une évaluation de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()

        eval = Evaluation(
            visuel=5,
            texture=5,
            pate=5,
            gout=5,
            description="Test Description",
            id_flan=flan.id_flan,
            id_user=user.id_user,
        )
        db.session.add(eval)
        db.session.commit()
        eval_id = eval.id_eval

    # Envoyer la requête de suppression
    response = client.post(f"/supprimer_evaluation/{eval_id}")
    assert response.status_code == 302  # Redirection

    # Vérifier que l'évaluation a été supprimée de la base de données
    with client.application.app_context():
        deleted_eval = db.session.get(Evaluation, eval_id)
        assert deleted_eval is None, "L'évaluation n'a pas été supprimée de la base de données"


def test_moyenne_evaluations_avec_calcul_automatique(client):
    """Test que la moyenne des évaluations s'affiche correctement même sans moyenne pré-calculée"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement et un flan de test
    with client.application.app_context():
        from flask_bcrypt import Bcrypt

        bcrypt = Bcrypt(client.application)
        etab = Etablissement(
            nom="Test Etablissement Moyenne",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(
            nom="Test Flan Moyenne",
            prix=3.0,
            id_etab=etab.id_etab,
            id_user=user.id_user,
        )
        db.session.add(flan)
        db.session.commit()

        # Créer une évaluation SANS moyenne pré-calculée (simule le bug original)
        eval1 = Evaluation(
            visuel=4.0,
            texture=4.5,
            pate=3.5,
            gout=4.0,
            moyenne=None,  # Pas de moyenne pré-calculée - cela simule le bug
            id_flan=flan.id_flan,
            id_user=user.id_user,
        )
        db.session.add(eval1)
        db.session.commit()

        # Tester que la moyenne s'affiche quand même
        moyenne_flan = flan.get_moyenne_evaluations()
        assert (
            moyenne_flan is not None
        ), "La moyenne ne devrait pas être None même sans moyenne pré-calculée"

        # Calculer la moyenne attendue manuellement
        expected_moyenne = round((4.0 + 4.5 + 3.5 + 4.0) / 4, 1)
        assert (
            moyenne_flan == expected_moyenne
        ), f"Moyenne attendue: {expected_moyenne}, obtenue: {moyenne_flan}"

        # Créer un deuxième utilisateur pour la deuxième évaluation
        # (car il y a une contrainte unique sur id_user + id_flan)
        user2 = Utilisateur(pseudo="testuser2", email="test2@example.com")
        user2.set_password("password", bcrypt)
        db.session.add(user2)
        db.session.commit()

        # Ajouter une deuxième évaluation avec moyenne pré-calculée
        eval2 = Evaluation(
            visuel=5.0,
            texture=5.0,
            pate=4.5,
            gout=5.0,
            moyenne=4.9,  # Moyenne pré-calculée
            id_flan=flan.id_flan,
            id_user=user2.id_user,
        )
        db.session.add(eval2)
        db.session.commit()

        # Tester que la moyenne globale est correcte
        nouvelle_moyenne = flan.get_moyenne_evaluations()
        assert (
            nouvelle_moyenne is not None
        ), "La moyenne ne devrait pas être None avec plusieurs évaluations"

        # La moyenne devrait être la moyenne des deux moyennes individuelles
        expected_global = round((expected_moyenne + 4.9) / 2, 1)
        assert (
            nouvelle_moyenne == expected_global
        ), f"Moyenne globale attendue: {expected_global}, obtenue: {nouvelle_moyenne}"

        # Créer un troisième utilisateur pour la troisième évaluation
        user3 = Utilisateur(pseudo="testuser3", email="test3@example.com")
        user3.set_password("password", bcrypt)
        db.session.add(user3)
        db.session.commit()

        # Tester avec une évaluation sans moyenne pré-calculée (mais avec tous les critères)
        # Cela simule le cas où une évaluation est créée via SQL direct sans calcul de moyenne
        eval3 = Evaluation(
            visuel=3.0,
            texture=3.5,  # Tous les critères sont présents
            pate=3.5,
            gout=4.0,
            moyenne=None,  # Mais la moyenne n'est pas pré-calculée
            id_flan=flan.id_flan,
            id_user=user3.id_user,
        )
        db.session.add(eval3)
        db.session.commit()

        # La moyenne devrait toujours s'afficher (calculée à la volée)
        moyenne_avec_manquants = flan.get_moyenne_evaluations()
        assert (
            moyenne_avec_manquants is not None
        ), "La moyenne devrait s'afficher même sans moyenne pré-calculée"

        # Vérifier que la moyenne est correcte
        expected_moyenne_eval3 = round((3.0 + 3.5 + 3.5 + 4.0) / 4, 1)
        # La moyenne globale devrait inclure cette nouvelle évaluation
        expected_global_final = round((expected_moyenne + 4.9 + expected_moyenne_eval3) / 3, 1)
        assert (
            abs(moyenne_avec_manquants - expected_global_final) < 0.1
        ), f"Moyenne globale finale attendue: {expected_global_final}, obtenue: {moyenne_avec_manquants}"


def test_dashboard_post_update_profile(client):
    """Test la mise à jour du profil via le dashboard"""
    user = client.application.config["TEST_USER"]

    # Envoyer une requête POST pour mettre à jour le profil
    response = client.post(
        "/dashboard",
        data={
            "profile-pseudo": "new_pseudo",
            "profile-email": "new_email@example.com",
            "profile-current_password": "password",
            "profile-new_password": "new_password",
            "profile-confirm_password": "new_password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier que le profil a été mis à jour
    with client.application.app_context():
        updated_user = db.session.get(Utilisateur, user.id_user)
        assert updated_user.pseudo == "new_pseudo"
        assert updated_user.email == "new_email@example.com"
        # Vérifier que le mot de passe a été mis à jour (on vérifie juste qu'il a changé)
        assert updated_user.password != user.password


def test_afficher_etablissement_unique_get(client):
    """Test l'affichage d'un établissement unique"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Accéder à la page de l'établissement
    response = client.get(f"/etablissement/{etab_id}")
    assert response.status_code == 200
    assert b"Test Etablissement" in response.data


def test_afficher_etablissement_unique_post_update(client):
    """Test la mise à jour d'un établissement"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Mettre à jour l'établissement
    response = client.post(
        f"/etablissement/{etab_id}",
        data={
            "edit-etab-nom": "Nouveau Nom",
            "edit-etab-description": "Nouvelle description",
            "edit-etab-adresse": "Nouvelle adresse",
            "edit-etab-ville": "Nouvelle ville",
            "edit-etab-code_postal": "69002",
            "edit-etab-latitude": "45.75",
            "edit-etab-longitude": "4.85",
            "edit-etab-type_etab": "BOULANGERIE",
            "edit-etab-statut_etablissement": "labellise",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier que l'établissement a été mis à jour
    with client.application.app_context():
        updated_etab = db.session.get(Etablissement, etab_id)
        assert updated_etab.nom == "Nouveau Nom"
        assert updated_etab.description == "Nouvelle description"


def test_afficher_flan_unique_get(client):
    """Test l'affichage d'un flan unique"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Accéder à la page du flan
    response = client.get(f"/flan/{flan_id}")
    assert response.status_code == 200
    assert b"Test Flan" in response.data


def test_afficher_flan_unique_post_update(client):
    """Test la mise à jour d'un flan"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement et un flan de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Test Flan", prix=2.5, id_etab=etab.id_etab, id_user=user.id_user)
        db.session.add(flan)
        db.session.commit()
        flan_id = flan.id_flan

    # Mettre à jour le flan
    response = client.post(
        f"/flan/{flan_id}",
        data={
            "edit-flan-nom": "Nouveau Flan",
            "edit-flan-description": "Nouvelle description",
            "edit-flan-prix": 3.0,
            "edit-flan-type_pate": "BRISEE",
            "edit-flan-type_saveur": "VANILLE",
            "edit-flan-type_texture": "CREMEUSE",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Vérifier que le flan a été mis à jour
    with client.application.app_context():
        updated_flan = db.session.get(Flan, flan_id)
        assert updated_flan.nom == "Nouveau Flan"
        assert updated_flan.prix == 3.0


def test_get_infowindow_content(client):
    """Test la route get_infowindow_content"""
    user = client.application.config["TEST_USER"]

    # Créer un établissement de test
    with client.application.app_context():
        etab = Etablissement(
            nom="Test Etablissement",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Test Ville",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Appeler la route pour obtenir le contenu de l'infowindow
    response = client.get(f"/get_infowindow_content?id_etab={etab_id}")
    assert response.status_code == 200
    assert b"Test Etablissement" in response.data


def test_liste_etablissements_avec_recherche_simple(client):
    """Test la route liste_etablissements avec une recherche simple"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie ABC",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Patisserie ABC",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Rechercher avec un terme qui correspond à un seul établissement -> redirection
    response = client.get(
        "/liste_etablissements?recherche_simple=Boulangerie", follow_redirects=False
    )
    assert response.status_code == 302  # Redirection car un seul résultat
    assert "/etablissement/" in response.location

    # Rechercher avec un terme qui correspond à une ville avec un seul établissement -> redirection
    response = client.get("/liste_etablissements?recherche_simple=Lyon", follow_redirects=False)
    assert response.status_code == 302  # Redirection car un seul résultat

    # Rechercher avec un terme qui correspond aux deux établissements -> liste
    response = client.get("/liste_etablissements?recherche_simple=ABC", follow_redirects=False)
    assert response.status_code == 200  # Pas de redirection car plusieurs résultats


@pytest.mark.main
@pytest.mark.performance
def test_liste_etablissements_avec_filtres_avances(client):
    """Test la route liste_etablissements avec des filtres avancés"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements et flans de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
            visite=True,
            label=False,
        )
        etab2 = Etablissement(
            nom="Patisserie Test",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Lyon",
            id_user=user.id_user,
            visite=False,
            label=True,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans pour les tests
        flan1 = Flan(
            nom="Flan Vanille",
            prix=2.0,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=user.id_user,
        )
        flan2 = Flan(
            nom="Flan Fruits",
            prix=3.5,
            type_pate="SABLEE",
            type_saveur="FRUITS",
            type_texture="GELATINEUSE",
            id_etab=etab2.id_etab,
            id_user=user.id_user,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

    # Test filtre par visite
    response = client.get("/liste_etablissements?visite=oui")
    assert response.status_code == 200
    assert b"Boulangerie Test" in response.data

    # Test filtre par labellisé
    response = client.get("/liste_etablissements?labellise=oui")
    assert response.status_code == 200
    assert b"Patisserie Test" in response.data

    # Test filtre par type de pâte
    response = client.get("/liste_etablissements?type_pate=BRISEE")
    assert response.status_code == 200
    assert b"Boulangerie Test" in response.data

    # Test filtre par type de saveur
    response = client.get("/liste_etablissements?type_saveur=FRUITS")
    assert response.status_code == 200
    assert b"Patisserie Test" in response.data

    # Test filtre par prix
    response = client.get("/liste_etablissements?prix=0")  # Moins de 2.5€
    assert response.status_code == 200
    assert b"Boulangerie Test" in response.data

    # Test filtre par type de texture
    response = client.get("/liste_etablissements?type_texture=CREMEUSE")
    assert response.status_code == 200
    assert b"Boulangerie Test" in response.data
    assert b"Patisserie Test" not in response.data

    response = client.get("/liste_etablissements?type_texture=GELATINEUSE")
    assert response.status_code == 200
    assert b"Patisserie Test" in response.data
    assert b"Boulangerie Test" not in response.data


def test_liste_etablissements_post_recherche(client):
    """Test la route liste_etablissements avec une recherche POST"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Autre Etablissement",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Rechercher avec une requête POST
    response = client.post("/liste_etablissements", data={"nom": "Boulangerie", "ville": "Lyon"})
    assert response.status_code == 200
    assert b"Boulangerie Test" in response.data


def test_liste_etablissements_cas_limites_valeurs_vides(client):
    """Test la route liste_etablissements avec des valeurs vides ou None"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Autre Etablissement",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Test avec des valeurs vides
    response = client.get(
        "/liste_etablissements",
        query_string={"nom": "", "ville": "", "visite": "", "labellise": ""},
    )
    assert response.status_code == 200
    # Devrait retourner tous les établissements
    assert b"Boulangerie Test" in response.data
    assert b"Autre Etablissement" in response.data


def test_liste_etablissements_cas_limites_caracteres_speciaux(client):
    """Test la route liste_etablissements avec des caractères spéciaux"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test avec des caractères spéciaux
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie 'L'Épi Doré'",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Café & Restaurant",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Test recherche avec caractères spéciaux - un seul résultat = redirection
    response = client.get(
        "/liste_etablissements", query_string={"recherche_simple": "Épi"}, follow_redirects=False
    )
    assert response.status_code == 302  # Redirection car un seul résultat
    assert "/etablissement/" in response.location

    response = client.get(
        "/liste_etablissements", query_string={"recherche_simple": "Café"}, follow_redirects=False
    )
    assert response.status_code == 302  # Redirection car un seul résultat
    assert "/etablissement/" in response.location

    # Test avec follow_redirects pour vérifier que la page de l'établissement se charge
    response = client.get(
        "/liste_etablissements", query_string={"recherche_simple": "Épi"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Boulangerie" in response.data


def test_liste_etablissements_cas_limites_aucune_correspondance(client):
    """Test la route liste_etablissements quand une recherche ne trouve rien"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Autre Etablissement",
            adresse="Autre Adresse",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Test 1: Recherche simple qui ne correspond à rien - affiche page sans résultats
    response = client.get(
        "/liste_etablissements", query_string={"recherche_simple": "Restaurant Inconnu"}
    )
    assert response.status_code == 200
    # Avec la nouvelle logique, recherche_simple filtre les établissements
    # Si rien ne correspond, la page s'affiche mais sans les établissements recherchés
    # La page doit quand même se charger correctement
    assert b"<!doctype html>" in response.data.lower() or b"<!DOCTYPE html>" in response.data

    # Test 2: Ville seule (sans autres filtres) - devrait afficher tous les établissements
    response = client.get("/liste_etablissements", query_string={"ville": "Marseille"})
    assert response.status_code == 200
    # Tous les établissements devraient être affichés (ville est utilisée pour centrer la carte)
    assert b"Boulangerie Test" in response.data
    assert b"Autre Etablissement" in response.data

    # Test 3: Filtres qui ne correspondent à rien - devrait filtrer et ne rien retourner
    response = client.get("/liste_etablissements", query_string={"visite": "oui"})
    assert response.status_code == 200
    # Aucun établissement ne devrait être affiché (filtre visite=oui est appliqué)
    assert b"Boulangerie Test" not in response.data
    assert b"Autre Etablissement" not in response.data


def test_liste_etablissements_cas_limites_valeurs_invalides(client):
    """Test la route liste_etablissements avec des valeurs invalides"""
    user = client.application.config["TEST_USER"]

    # Créer des établissements de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="Test Adresse",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
        )
        db.session.add(etab1)
        db.session.commit()

    # Test avec des valeurs invalides pour les filtres
    response = client.get(
        "/liste_etablissements",
        query_string={
            "visite": "invalide",  # Valeur invalide pour visite
            "labellise": "peut-etre",  # Valeur invalide pour labellise
            "prix": "inconnu",  # Valeur invalide pour prix
        },
    )
    assert response.status_code == 200
    # Devrait gérer les valeurs invalides gracieusement et retourner les résultats
    # ou ignorer les filtres invalides


def test_rechercher_route(client):
    """Test la route rechercher"""
    response = client.get("/rechercher")
    assert response.status_code == 200
    assert b"Rechercher" in response.data


def test_index_route(client):
    """Test la route index"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"PlanFlan" in response.data


def test_filtrer_etablissements_directement(client):
    """Test la fonction filtrer_etablissements directement"""
    from app.routes.main import filtrer_etablissements

    user = client.application.config["TEST_USER"]

    # Créer des données de test
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie A",
            adresse="Test",
            code_postal="69001",
            ville="Lyon",
            id_user=user.id_user,
            visite=True,
        )
        etab2 = Etablissement(
            nom="Boulangerie B",
            adresse="Test",
            code_postal="69002",
            ville="Paris",
            id_user=user.id_user,
            visite=False,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer la requête de base
        query = Etablissement.query

        # Tester le filtre par nom
        filtered = filtrer_etablissements(query, nom="Boulangerie A")
        results = filtered.all()
        assert len(results) == 1
        assert results[0].nom == "Boulangerie A"

        # Tester le filtre par ville
        filtered = filtrer_etablissements(query, ville="Paris")
        results = filtered.all()
        assert len(results) == 1
        assert results[0].ville == "Paris"

        # Tester le filtre par visite
        filtered = filtrer_etablissements(query, visite="oui")
        results = filtered.all()
        assert len(results) == 1
        assert results[0].visite == True

        # Tester le filtre par labellisé
        filtered = filtrer_etablissements(query, labellise="non")
        results = filtered.all()
        assert len(results) == 2  # Aucun n'est labellisé


def test_formulaire_evaluation_avec_selectfield(client):
    """Test EvalForm avec SelectField pour les notes."""
    with client.application.app_context():
        form = EvalForm()

        # Vérifier que les champs sont bien des SelectField
        from wtforms.fields import SelectField

        assert isinstance(form.visuel, SelectField)
        assert isinstance(form.texture, SelectField)
        assert isinstance(form.pate, SelectField)
        assert isinstance(form.gout, SelectField)

        # Vérifier que les choix sont corrects
        # Format uniforme avec toujours .0 pour les entiers
        valid_choices = [
            "0.0",
            "0.5",
            "1.0",
            "1.5",
            "2.0",
            "2.5",
            "3.0",
            "3.5",
            "4.0",
            "4.5",
            "5.0",
        ]
        assert form.visuel.choices == [(choice, choice) for choice in valid_choices]
        assert form.texture.choices == [(choice, choice) for choice in valid_choices]
        assert form.pate.choices == [(choice, choice) for choice in valid_choices]
        assert form.gout.choices == [(choice, choice) for choice in valid_choices]

        # Tester avec des données valides
        # Format uniforme avec .0 pour les entiers
        form.visuel.data = "4.5"
        form.texture.data = "3.0"  # Format uniforme avec .0
        form.pate.data = "5.0"  # Format uniforme avec .0
        form.gout.data = "2.5"
        form.description.data = "Test evaluation avec SelectField"

        # Le formulaire devrait être valide
        # Note: La validation CSRF est désactivée pour ce test unitaire
        assert form.validate()

        # Vérifier que les données sont bien des chaînes
        assert isinstance(form.visuel.data, str)
        assert isinstance(form.texture.data, str)
        assert isinstance(form.pate.data, str)
        assert isinstance(form.gout.data, str)

        # Vérifier que les valeurs sont parmi les choix valides
        assert form.visuel.data in valid_choices
        assert form.texture.data in valid_choices
        assert form.pate.data in valid_choices
        assert form.gout.data in valid_choices


"""
Tests approfondis pour les fonctions principales de main.py
Ces tests visent à améliorer la couverture en testant les branches
conditionnelles et les cas d'erreur non couverts par les tests existants.
"""

from app import db
from app.models import Etablissement, Flan
from app.routes.main import filtrer_etablissements


class TestFiltrerEtablissements:
    """Tests approfondis pour la fonction filtrer_etablissements."""

    def test_filtrer_par_nom(self, client):
        """Test le filtrage par nom d'établissement."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, nom="Boulangerie")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].nom == "Boulangerie Martin"

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_ville(self, client):
        """Test le filtrage par ville."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, ville="Lyon")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].nom == "Patisserie Dubois"

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_visite_oui(self, client):
        """Test le filtrage par établissement visité (oui)."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
            visite=True,
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
            visite=False,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, visite="oui")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].visite == True

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_visite_non(self, client):
        """Test le filtrage par établissement non visité."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
            visite=True,
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
            visite=False,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, visite="non")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].visite == False

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_labellise_oui(self, client):
        """Test le filtrage par établissement labellisé."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
            label=True,
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
            label=False,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, labellise="oui")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].label == True

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_labellise_non(self, client):
        """Test le filtrage par établissement non labellisé."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
            label=True,
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
            label=False,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query, labellise="non")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].label == False

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_type_pate(self, client):
        """Test le filtrage par type de pâte."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="FONDANTE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan3 = Flan(
            nom="Flan Citron",
            prix=2.5,
            type_pate="BRISEE",
            type_saveur="FRUITS",
            type_texture="CREMEUSE",
            id_etab=etab2.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2, flan3])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, type_pate="BRISEE")
        results = filtered.all()

        # Devrait retourner les établissements avec des flans à pâte brisée
        assert len(results) == 2  # Boulangerie Martin et Patisserie Dubois

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(flan3)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_type_saveur(self, client):
        """Test le filtrage par type de saveur."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="FONDANTE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, type_saveur="VANILLE")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].nom == "Boulangerie Martin"

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()


# Tests pour améliorer la couverture des routes principales
@pytest.mark.routes
def test_index_route(client):
    """Test la route d'accueil"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"PlanFlan" in response.data or b"planflan" in response.data


@pytest.mark.routes
def test_dashboard_route_authenticated(client):
    """Test que le dashboard est accessible quand authentifié"""
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    # Devrait montrer le tableau de bord
    assert b"Tableau de bord" in response.data or b"Dashboard" in response.data


@pytest.mark.routes
def test_proposer_etablissement_route_authenticated(client):
    """Test que la page de proposition d'établissement est accessible quand authentifié"""
    response = client.get("/proposer_etablissement", follow_redirects=True)
    assert response.status_code == 200
    # Devrait montrer le formulaire de proposition avec champ de recherche
    assert b"Recherche" in response.data or b"recherche" in response.data


@pytest.mark.routes
def test_liste_etablissements_route(client):
    """Test la route de liste des établissements"""
    response = client.get("/liste_etablissements")
    assert response.status_code == 200
    assert b"Etablissement" in response.data or b"etablissement" in response.data


@pytest.mark.routes
def test_rechercher_route(client):
    """Test la route de recherche"""
    response = client.get("/rechercher")
    assert response.status_code == 200
    assert b"Recherche" in response.data or b"recherche" in response.data


# Tests pour les routes d'établissements
@pytest.mark.routes
def test_etablissement_creation_get(client):
    """Test la route GET pour la création d'établissement"""
    response = client.get("/proposer_etablissement", follow_redirects=True)
    assert response.status_code == 200
    # Devrait montrer le formulaire de création
    assert b"Recherche" in response.data or b"recherche" in response.data


# Tests pour les routes API manquantes
@pytest.mark.api
def test_api_villes_sans_parametre(client):
    """Test l'API /api/villes sans paramètre de recherche"""
    # Appeler l'API sans paramètre
    response = client.get("/api/villes")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    # L'API retourne les 20 villes les plus peuplées de France (données statiques)
    assert len(data) == 20
    # Vérifier que les grandes villes sont présentes
    assert "Paris" in data
    assert "Marseille" in data
    assert "Lyon" in data
    assert "Toulouse" in data
    assert "Nice" in data


@pytest.mark.api
def test_api_villes_avec_parametre(client):
    """Test l'API /api/villes avec paramètre de recherche"""
    # Appeler l'API avec paramètre de recherche
    response = client.get("/api/villes?q=ly")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    assert "Lyon" in data
    assert "Marseille" not in data  # Ne devrait pas être dans les résultats

    # Test avec un autre paramètre
    response = client.get("/api/villes?q=par")
    assert response.status_code == 200
    data = response.get_json()
    assert "Paris" in data
    assert "Lyon" not in data


@pytest.mark.api
def test_api_villes_aucune_correspondance(client):
    """Test l'API /api/villes quand aucune ville ne correspond"""
    # Appeler l'API avec un paramètre qui ne correspond à rien
    response = client.get("/api/villes?q=zzz")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0  # Aucune correspondance


@pytest.mark.api
def test_api_etablissements_search_sans_parametre(client):
    """Test l'API /api/etablissements/search sans paramètre de recherche"""
    response = client.get("/api/etablissements/search")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0  # Minimum 2 caractères requis


@pytest.mark.api
def test_api_etablissements_search_query_trop_courte(client):
    """Test l'API /api/etablissements/search avec une requête trop courte"""
    response = client.get("/api/etablissements/search?q=a")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0  # Minimum 2 caractères requis


@pytest.mark.api
def test_api_etablissements_search_avec_resultats(client):
    """Test l'API /api/etablissements/search avec des résultats"""
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        # Créer des établissements de test
        etab1 = Etablissement(
            nom="Boulangerie du Marché",
            ville="Lyon",
            adresse="123 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Pâtisserie Parisienne",
            ville="Paris",
            adresse="456 Rue Test",
            code_postal="75001",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Invalider le cache pour les tests
        from app.routes.main import invalidate_etablissements_search_cache

        invalidate_etablissements_search_cache()

    # Recherche par nom
    response = client.get("/api/etablissements/search?q=boulangerie")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert any("Boulangerie" in etab["nom"] for etab in data)
    # Vérifier la structure des données
    assert "id_etab" in data[0]
    assert "nom" in data[0]
    assert "ville" in data[0]
    assert "url" in data[0]
    assert "total_count" in data[0]

    # Recherche par ville
    response = client.get("/api/etablissements/search?q=paris")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert any("Paris" in etab["ville"] for etab in data)


@pytest.mark.api
def test_api_etablissements_search_aucun_resultat(client):
    """Test l'API /api/etablissements/search quand aucun établissement ne correspond"""
    response = client.get("/api/etablissements/search?q=zzzzzzz")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.api
def test_api_etablissements_search_tri_pertinence(client):
    """Test le tri par pertinence dans /api/etablissements/search"""
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        # Créer des établissements avec différentes correspondances
        etab1 = Etablissement(
            nom="Café Central",
            ville="Lyon",
            adresse="1 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Restaurant Le Café",
            ville="Paris",
            adresse="2 Rue Test",
            code_postal="75001",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        from app.routes.main import invalidate_etablissements_search_cache

        invalidate_etablissements_search_cache()

    response = client.get("/api/etablissements/search?q=café")
    assert response.status_code == 200
    data = response.get_json()
    # Les établissements commençant par "Café" devraient être en premier
    if len(data) >= 2:
        first_nom = data[0]["nom"].lower()
        assert first_nom.startswith("café")


def test_recherche_simple_redirection_unique(client):
    """Test la redirection automatique vers l'établissement unique"""
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        # Créer un établissement avec un nom unique
        etab = Etablissement(
            nom="Établissement Unique XYZ123",
            ville="Marseille",
            adresse="789 Rue Unique",
            code_postal="13001",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()
        etab_id = etab.id_etab

    # Rechercher avec un terme qui ne correspond qu'à cet établissement
    response = client.get("/liste_etablissements?recherche_simple=XYZ123", follow_redirects=False)
    assert response.status_code == 302  # Redirection
    assert f"/etablissement/{etab_id}" in response.location


def test_recherche_simple_plusieurs_resultats(client):
    """Test que la recherche simple ne redirige pas s'il y a plusieurs résultats"""
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        # Créer plusieurs établissements avec un terme commun
        etab1 = Etablissement(
            nom="Boulangerie Test Multiple A",
            ville="Lyon",
            adresse="1 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
        )
        etab2 = Etablissement(
            nom="Boulangerie Test Multiple B",
            ville="Paris",
            adresse="2 Rue Test",
            code_postal="75001",
            id_user=user.id_user,
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

    # Rechercher avec un terme qui correspond à plusieurs établissements
    response = client.get("/liste_etablissements?recherche_simple=Multiple", follow_redirects=False)
    assert response.status_code == 200  # Pas de redirection, affiche la liste


def test_invalidation_cache_etablissements(client):
    """Test l'invalidation du cache lors de l'ajout d'un établissement"""
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        from app.routes.main import (
            api_etablissements_search,
            invalidate_etablissements_search_cache,
        )

        # Forcer la création du cache
        invalidate_etablissements_search_cache()

        # Créer un établissement unique
        etab = Etablissement(
            nom="Nouveau Test Cache ABC",
            ville="Bordeaux",
            adresse="999 Rue Cache",
            code_postal="33000",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        # Le cache devrait avoir été invalidé par le signal SQLAlchemy
        # Vérifier en faisant une recherche

    response = client.get("/api/etablissements/search?q=Cache ABC")
    assert response.status_code == 200
    data = response.get_json()
    # Le nouvel établissement devrait être trouvé
    assert any("Cache ABC" in etab["nom"] for etab in data)


@pytest.mark.api
def test_api_etablissements_get(client):
    """Test l'API /api/etablissements avec méthode GET"""
    # Créer des établissements et flans de test
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            ville="Lyon",
            adresse="123 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
            visite=True,
            label=False,
        )
        etab2 = Etablissement(
            nom="Patisserie Test",
            ville="Paris",
            adresse="456 Rue Test",
            code_postal="75001",
            id_user=user.id_user,
            visite=False,
            label=True,
        )

        # D'abord, ajouter et commiter les établissements pour obtenir leurs IDs
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Ensuite, créer les flans avec les IDs des établissements
        # Note: L'API utilise un JOIN avec Flan, donc chaque établissement doit avoir au moins un flan
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=user.id_user,
        )

        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="CREMEUSE",
            id_etab=etab2.id_etab,
            id_user=user.id_user,
        )

        db.session.add_all([flan1, flan2])
        db.session.commit()

    # Appeler l'API GET sans filtres
    response = client.get("/api/etablissements")
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2  # Les deux établissements

    # Vérifier la structure des données
    for etab_data in data:
        assert "id_etab" in etab_data
        assert "nom" in etab_data
        assert "ville" in etab_data
        assert "flans" in etab_data

    # Nettoyage
    with client.application.app_context():
        db.session.delete(flan1)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()


@pytest.mark.api
def test_api_etablissements_post(client):
    """Test l'API /api/etablissements avec méthode POST et filtres"""
    # Créer des établissements et flans de test
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Lyon",
            ville="Lyon",
            adresse="123 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
            visite=True,
            label=False,
        )
        etab2 = Etablissement(
            nom="Patisserie Paris",
            ville="Paris",
            adresse="456 Rue Test",
            code_postal="75001",
            id_user=user.id_user,
            visite=False,
            label=True,
        )

        # D'abord, ajouter et commiter les établissements pour obtenir leurs IDs
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Ensuite, créer les flans avec les IDs des établissements
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=user.id_user,
        )

        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="MIX_PARFAIT",
            id_etab=etab2.id_etab,
            id_user=user.id_user,
        )

        db.session.add_all([flan1, flan2])
        db.session.commit()

    # Appeler l'API POST avec des filtres
    response = client.post(
        "/api/etablissements",
        json={"ville": "Lyon", "visite": "oui", "type_pate": "BRISEE"},
    )
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1  # Un seul établissement correspond
    assert data[0]["nom"] == "Boulangerie Lyon"
    assert data[0]["ville"] == "Lyon"

    # Test avec filtre par type de saveur
    response = client.post("/api/etablissements", json={"type_saveur": "CHOCOLAT"})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["nom"] == "Patisserie Paris"

    # Nettoyage
    with client.application.app_context():
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()


@pytest.mark.api
def test_api_etablissements_aucune_correspondance(client):
    """Test l'API /api/etablissements quand aucun établissement ne correspond"""
    # Créer un établissement de test
    user = client.application.config["TEST_USER"]
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Test",
            ville="Lyon",
            adresse="123 Rue Test",
            code_postal="69001",
            id_user=user.id_user,
        )
        db.session.add(etab1)
        db.session.commit()

    # Appeler l'API avec des filtres qui ne correspondent à rien
    response = client.post("/api/etablissements", json={"ville": "Marseille", "visite": "oui"})
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0  # Aucune correspondance

    # Nettoyage
    with client.application.app_context():
        db.session.delete(etab1)
        db.session.commit()

    def test_filtrer_par_type_texture(self, client):
        """Test le filtrage par type de texture."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="FONDANTE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, type_texture="FONDANTE")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].nom == "Boulangerie Martin"

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_prix_0(self, client):
        """Test le filtrage par prix < 2.5."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Citron",
            prix=2.0,
            type_pate="BRISEE",
            type_saveur="FRUITS",
            type_texture="CREMEUSE",
            id_etab=etab2.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, prix="0")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].nom == "Patisserie Dubois"  # Flan Citron à 2.0€

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_prix_2_5(self, client):
        """Test le filtrage par prix entre 2.5 et 5."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Citron",
            prix=2.5,
            type_pate="BRISEE",
            type_saveur="FRUITS",
            type_texture="CREMEUSE",
            id_etab=etab2.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, prix="2.5")
        results = filtered.all()

        # Devrait retourner les deux établissements (Flan Vanille à 3.5€ et Flan Citron à 2.5€)
        assert len(results) == 2

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_par_prix_5(self, client):
        """Test le filtrage par prix >= 5."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        db.session.add(etab1)
        db.session.commit()

        # Créer un flan
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        db.session.add(flan1)
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, prix="5")
        results = filtered.all()

        # Aucun flan dans nos données de test n'a un prix >= 5
        assert len(results) == 0

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(etab1)
        db.session.commit()

    def test_filtrer_combinaison_criteres(self, client):
        """Test le filtrage avec une combinaison de critères."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Citron",
            prix=2.5,
            type_pate="BRISEE",
            type_saveur="FRUITS",
            type_texture="CREMEUSE",
            id_etab=etab2.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        filtered = filtrer_etablissements(query, ville="Paris", type_pate="BRISEE", prix="2.5")
        results = filtered.all()

        # Devrait retourner Boulangerie Martin (Flan Vanille)
        assert len(results) == 1
        assert results[0].nom == "Boulangerie Martin"

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()


class TestCasErreur:
    """Tests pour les cas d'erreur et exceptions."""

    def test_etablissement_inexistant(self, client):
        """Test l'accès à un établissement inexistant."""
        response = client.get("/etablissement/99999")
        assert response.status_code == 404

    def test_flan_inexistant(self, client):
        """Test l'accès à un flan inexistant."""
        response = client.get("/flan/99999")
        assert response.status_code == 404

    def test_evaluation_inexistante(self, client):
        """Test l'accès à une évaluation inexistante."""
        response = client.get("/evaluation/99999")
        assert response.status_code == 404


class TestFonctionsUtilitaires:
    """Tests pour les fonctions utilitaires dans main.py."""

    def test_filtrer_etablissements_sans_criteres(self, client):
        """Test filtrer_etablissements sans critères."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        query = Etablissement.query
        filtered = filtrer_etablissements(query)
        results = filtered.all()

        # Devrait retourner tous les établissements
        assert len(results) == 2

        # Nettoyage
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()

    def test_filtrer_etablissements_critere_tous(self, client):
        """Test filtrer_etablissements avec critère 'tous'."""
        # Créer des données de test
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            ville="Paris",
            adresse="123 Rue de Paris",
            code_postal="75001",
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            ville="Lyon",
            adresse="456 Rue de Lyon",
            code_postal="69001",
        )
        db.session.add_all([etab1, etab2])
        db.session.commit()

        # Créer des flans pour chaque établissement
        flan1 = Flan(
            nom="Flan Vanille",
            prix=3.5,
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            id_etab=etab1.id_etab,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Chocolat",
            prix=4.0,
            type_pate="SABLEE",
            type_saveur="CHOCOLAT",
            type_texture="MIX_PARFAIT",
            id_etab=etab2.id_etab,
            id_user=1,
        )
        db.session.add_all([flan1, flan2])
        db.session.commit()

        query = Etablissement.query.join(Flan)
        # Le critère 'tous' ne devrait pas filtrer
        filtered = filtrer_etablissements(query, type_pate="tous")
        results = filtered.all()

        # Devrait retourner tous les établissements avec flans (2 établissements distincts)
        assert len(results) == 2

        # Nettoyage
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(etab1)
        db.session.delete(etab2)
        db.session.commit()
