"""Tests pour les fonctions utilitaires (outils.py)

Ce module teste les fonctions utilitaires de l'application PlanFlan,
incluant les fonctions de calcul de distance, suppression d'accents,
vérification CSRF, et gestion des photos Google Places.
"""

from app.outils import (
    calculer_distance,
    afficher_etablissements,
    enlever_accents,
    verifier_csrf_token,
    verifier_csrf_ou_renvoyer_erreur,
    get_place_details,
    fetch_place_photos,
)
from app.models import Etablissement, Flan
from app import db, create_app
from app.config import TestConfig
from unittest.mock import patch, MagicMock
import pytest
import os


@pytest.mark.parametrize(
    "test_name,lat1,lon1,lat2,lon2,expected_min,expected_max",
    [
        # Test 1: Same location (should be 0)
        ("same_location", 45.75, 4.85, 45.75, 4.85, 0.0, 0.0),
        # Test 2: Close locations (Lyon center to Lyon Part-Dieu)
        ("close_locations", 45.7578, 4.8351, 45.7544, 4.8586, 0, 5),
        # Test 3: Lyon to Paris
        ("lyon_to_paris", 45.7578, 4.8351, 48.8566, 2.3522, 300, 500),
    ],
)
@pytest.mark.utils
def test_calculer_distance_parametrize(
    test_name, lat1, lon1, lat2, lon2, expected_min, expected_max
):
    """Test calculer_distance avec différents scénarios (paramétrisé)"""
    distance = calculer_distance(lat1, lon1, lat2, lon2)

    # Vérifier que la distance est dans la plage attendue
    assert expected_min <= distance <= expected_max, (
        f"Test {test_name} failed: expected distance between {expected_min} and {expected_max}, "
        f"got {distance}"
    )

    # Pour les cas où la distance devrait être exactement 0
    if expected_min == expected_max == 0.0:
        assert distance == 0.0, f"Test {test_name} failed: expected exact 0.0, got {distance}"


@pytest.mark.utils
@pytest.mark.parametrize(
    "test_name,input_text,expected_output",
    [
        # Basic French accents
        ("basic_french", "Café", "Cafe"),
        ("hotel", "Hôtel", "Hotel"),
        ("ete", "Été", "Ete"),
        ("a_propos", "À propos", "A propos"),
        ("etre", "Être ou ne pas être", "Etre ou ne pas etre"),
        # Special characters
        ("ca_va", "Ça va", "Ca va"),
        ("mur", "Mûr", "Mur"),
        # No accents
        ("no_accents", "Hello World", "Hello World"),
        ("numbers", "12345", "12345"),
        ("empty", "", ""),
    ],
)
def test_enlever_accents_parametrize(test_name, input_text, expected_output):
    """Test enlever_accents avec différents scénarios (paramétrisé)"""
    resultat = enlever_accents(input_text)
    assert (
        resultat == expected_output
    ), f"Test {test_name} failed: expected '{expected_output}', got '{resultat}'"


def test_afficher_etablissements_vide():
    """Test afficher_etablissements avec une liste vide"""
    etablissements, etablissements_json = afficher_etablissements([])
    assert etablissements == []
    assert etablissements_json == []


def test_afficher_etablissements_avec_donnees(client):
    """Test afficher_etablissements avec des établissements réels"""
    # Créer des établissements et flans de test
    with client.application.app_context():
        # Créer un établissement avec un flan
        etab1 = Etablissement(
            nom="Boulangerie Test",
            adresse="1 Rue Test",
            code_postal="69001",
            ville="Lyon",
            latitude=45.75,
            longitude=4.85,
            id_user=1,
        )
        db.session.add(etab1)
        db.session.commit()

        flan1 = Flan(nom="Flan Vanille", prix=2.5, id_etab=etab1.id_etab, id_user=1)
        db.session.add(flan1)
        db.session.commit()

        # Créer un établissement sans flan
        etab2 = Etablissement(
            nom="Patisserie Test",
            adresse="2 Rue Test",
            code_postal="69002",
            ville="Lyon",
            latitude=45.76,
            longitude=4.86,
            id_user=1,
        )
        db.session.add(etab2)
        db.session.commit()

        # Récupérer les établissements pour le test
        etablissements = [etab1, etab2]

        # Appeler la fonction DANS le contexte de la session
        result_etab, result_json = afficher_etablissements(etablissements)

    # Vérifications
    assert len(result_etab) == 2
    assert len(result_json) == 2

    # Vérifier que les établissements sont bien retournés
    assert result_etab[0].nom == "Boulangerie Test"
    assert result_etab[1].nom == "Patisserie Test"

    # Vérifier la structure JSON de base
    for etab_json in result_json:
        assert "id_etab" in etab_json
        assert "nom" in etab_json
        assert "adresse" in etab_json
        assert "ville" in etab_json
        assert "code_postal" in etab_json
        assert "latitude" in etab_json
        assert "longitude" in etab_json
        # Vérifier que les flans sont inclus si présents
        if etab_json["nom"] == "Boulangerie Test":
            assert "flans" in etab_json
            assert len(etab_json["flans"]) > 0
        else:
            assert "flans" in etab_json


# Tests pour les fonctions CSRF manquantes


@pytest.mark.utils
def test_enlever_accents_avec_none():
    """Test enlever_accents avec une valeur None"""
    resultat = enlever_accents(None)
    assert resultat == ""  # Devrait retourner une chaîne vide


@pytest.mark.utils
def test_enlever_accents_cas_mixte_et_speciaux():
    """Test enlever_accents avec un mélange complexe de cas et caractères spéciaux"""
    texte_complexe = "L'Été 2025 à PARIS: Café @ 3,50€, Hôtel 5★, Être ou ne pas être!"
    resultat = enlever_accents(texte_complexe)

    # Vérifier que les accents sont supprimés mais que la casse et les caractères ASCII sont préservés
    assert "L'Ete 2025 a PARIS: Cafe @ 3,50, Hotel 5, Etre ou ne pas etre!" == resultat

    # Vérifier que certains mots spécifiques sont présents
    assert "Ete" in resultat
    assert "PARIS" in resultat  # La casse devrait être préservée
    assert "Cafe" in resultat
    assert "Hotel" in resultat
    assert "3,50" in resultat
    assert "5" in resultat
    assert "Etre" in resultat


@pytest.mark.utils
def test_enlever_accents_avec_nombres():
    """Test enlever_accents avec des nombres et caractères spéciaux"""
    assert enlever_accents("12345") == "12345"
    assert enlever_accents("Prix: 3,50€") == "Prix: 3,50"  # Le symbole € est supprimé car non ASCII
    assert enlever_accents("Taux: 10%") == "Taux: 10%"


@pytest.mark.utils
def test_afficher_etablissements_avec_flans_multiples(client):
    """Test afficher_etablissements avec plusieurs flans par établissement"""
    # Créer un établissement avec plusieurs flans
    with client.application.app_context():
        etab1 = Etablissement(
            nom="Boulangerie Multi-Flans",
            adresse="1 Rue Test",
            code_postal="69001",
            ville="Lyon",
            latitude=45.75,
            longitude=4.85,
            id_user=1,
        )
        db.session.add(etab1)
        db.session.commit()

        # Ajouter plusieurs flans
        flan1 = Flan(nom="Flan Vanille", prix=2.5, id_etab=etab1.id_etab, id_user=1)
        flan2 = Flan(nom="Flan Chocolat", prix=3.0, id_etab=etab1.id_etab, id_user=1)
        flan3 = Flan(nom="Flan Caramel", prix=3.5, id_etab=etab1.id_etab, id_user=1)
        db.session.add_all([flan1, flan2, flan3])
        db.session.commit()

        # Appeler la fonction
        result_etab, result_json = afficher_etablissements([etab1])

    # Vérifications
    assert len(result_etab) == 1
    assert len(result_json) == 1

    # Vérifier que tous les flans sont inclus
    etab_json = result_json[0]
    assert "flans" in etab_json
    assert len(etab_json["flans"]) == 3

    # Vérifier les noms des flans
    flan_noms = [flan["nom"] for flan in etab_json["flans"]]
    assert "Flan Vanille" in flan_noms
    assert "Flan Chocolat" in flan_noms
    assert "Flan Caramel" in flan_noms

    # Nettoyage
    with client.application.app_context():
        db.session.delete(flan1)
        db.session.delete(flan2)
        db.session.delete(flan3)
        db.session.delete(etab1)
        db.session.commit()


# ============================================================================
# Tests pour les fonctions CSRF
# ============================================================================


@pytest.mark.utils
class TestVerifierCsrfToken:
    """Tests pour la fonction verifier_csrf_token"""

    def test_verifier_csrf_token_methode_get(self, client):
        """Test que les méthodes GET ne nécessitent pas de token CSRF"""
        with client.application.test_request_context("/test", method="GET"):
            valide, message = verifier_csrf_token()
            assert valide is True
            assert message is None

    def test_verifier_csrf_token_methode_head(self, client):
        """Test que les méthodes HEAD ne nécessitent pas de token CSRF"""
        with client.application.test_request_context("/test", method="HEAD"):
            valide, message = verifier_csrf_token()
            assert valide is True
            assert message is None

    def test_verifier_csrf_token_methode_options(self, client):
        """Test que les méthodes OPTIONS ne nécessitent pas de token CSRF"""
        with client.application.test_request_context("/test", method="OPTIONS"):
            valide, message = verifier_csrf_token()
            assert valide is True
            assert message is None

    def test_verifier_csrf_token_mode_testing(self, client):
        """Test que le mode TESTING désactive la vérification CSRF"""
        with client.application.test_request_context("/test", method="POST"):
            # En mode TESTING, le token CSRF devrait être validé automatiquement
            valide, message = verifier_csrf_token()
            assert valide is True
            assert message is None

    def test_verifier_csrf_token_post_sans_token(self):
        """Test que POST sans token CSRF échoue en mode production"""
        app = create_app(TestConfig)
        app.config["TESTING"] = False  # Désactiver le mode test
        app.config["WTF_CSRF_ENABLED"] = True

        with app.test_request_context("/test", method="POST"):
            valide, message = verifier_csrf_token()
            assert valide is False
            assert "Token CSRF manquant" in message

    def test_verifier_csrf_token_post_avec_token_invalide(self):
        """Test que POST avec token CSRF invalide échoue"""
        app = create_app(TestConfig)
        app.config["TESTING"] = False
        app.config["WTF_CSRF_ENABLED"] = True

        with app.test_request_context(
            "/test",
            method="POST",
            headers={"X-CSRFToken": "invalid-token-123"},
        ):
            valide, message = verifier_csrf_token()
            assert valide is False
            assert "Token CSRF invalide" in message


@pytest.mark.utils
class TestVerifierCsrfOuRenvoyerErreur:
    """Tests pour la fonction verifier_csrf_ou_renvoyer_erreur"""

    def test_verifier_csrf_ou_renvoyer_erreur_valide(self, client):
        """Test avec un token CSRF valide (mode test)"""
        with client.application.test_request_context("/test", method="POST"):
            valide, response = verifier_csrf_ou_renvoyer_erreur()
            assert valide is True
            assert response is None

    def test_verifier_csrf_ou_renvoyer_erreur_invalide(self):
        """Test avec un token CSRF invalide"""
        app = create_app(TestConfig)
        app.config["TESTING"] = False
        app.config["WTF_CSRF_ENABLED"] = True

        with app.test_request_context("/test", method="POST"):
            valide, response = verifier_csrf_ou_renvoyer_erreur()
            assert valide is False
            assert response is not None
            # La réponse devrait être un tuple (jsonify, 403)
            json_response, status_code = response
            assert status_code == 403


# ============================================================================
# Tests pour les fonctions Google Places API
# ============================================================================


@pytest.mark.utils
class TestGetPlaceDetails:
    """Tests pour la fonction get_place_details"""

    def test_get_place_details_succes(self, client):
        """Test récupération réussie des détails d'un lieu"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"photos": [{"photo_reference": "ref123", "width": 400, "height": 300}]}
        }

        with client.application.app_context():
            with patch("app.outils.requests.get", return_value=mock_response):
                result = get_place_details("ChIJTest123", "fake-api-key")
                assert result is not None
                assert "photos" in result
                assert len(result["photos"]) == 1

    def test_get_place_details_erreur_http(self, client):
        """Test gestion d'une erreur HTTP"""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with client.application.app_context():
            with patch("app.outils.requests.get", return_value=mock_response):
                result = get_place_details("ChIJInvalid", "fake-api-key")
                assert result is None

    def test_get_place_details_exception_reseau(self, client):
        """Test gestion d'une exception réseau"""
        with client.application.app_context():
            with patch(
                "app.outils.requests.get",
                side_effect=Exception("Network error"),
            ):
                result = get_place_details("ChIJTest123", "fake-api-key")
                assert result is None

    def test_get_place_details_pas_de_result(self, client):
        """Test quand la réponse ne contient pas de 'result'"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ZERO_RESULTS"}

        with client.application.app_context():
            with patch("app.outils.requests.get", return_value=mock_response):
                result = get_place_details("ChIJEmpty", "fake-api-key")
                assert result is None


@pytest.mark.utils
class TestFetchPlacePhotos:
    """Tests pour la fonction fetch_place_photos"""

    def test_fetch_place_photos_sans_place_id(self, client):
        """Test avec un place_id None"""
        with client.application.app_context():
            result = fetch_place_photos(1, None, "fake-api-key")
            assert result == []

    def test_fetch_place_photos_fichiers_existants(self, client):
        """Test quand les fichiers photos existent déjà"""
        with client.application.app_context():
            # Créer un établissement de test
            etab = Etablissement(
                nom="Test Boulangerie",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                google_place_id="ChIJExisting123",
                id_user=1,
            )
            db.session.add(etab)
            db.session.commit()

            # Créer un fichier temporaire simulant une photo existante
            upload_folder = client.application.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)

            filename = "ChIJExisting123_photo_0.jpg"
            filepath = os.path.join(upload_folder, filename)

            # Créer un fichier factice
            with open(filepath, "wb") as f:
                f.write(b"fake image content")

            try:
                result = fetch_place_photos(etab.id_etab, "ChIJExisting123", "fake-api-key")
                assert len(result) == 1
                assert "ChIJExisting123_photo_0.jpg" in result
            finally:
                # Nettoyage
                if os.path.exists(filepath):
                    os.remove(filepath)
                db.session.delete(etab)
                db.session.commit()

    def test_fetch_place_photos_pas_de_photos_disponibles(self, client):
        """Test quand aucune photo n'est disponible dans l'API"""
        with client.application.app_context():
            with patch("app.outils.get_place_details", return_value={}):
                result = fetch_place_photos(1, "ChIJNoPhotos", "fake-api-key")
                assert result == []


# ============================================================================
# Tests supplémentaires pour calculer_distance
# ============================================================================


@pytest.mark.utils
@pytest.mark.parametrize(
    "test_name,lat1,lon1,lat2,lon2",
    [
        ("string_coords", "45.75", "4.85", "45.76", "4.86"),
        ("mixed_types", 45.75, "4.85", "45.76", 4.86),
    ],
)
def test_calculer_distance_avec_strings(test_name, lat1, lon1, lat2, lon2):
    """Test que calculer_distance gère les coordonnées en string"""
    distance = calculer_distance(lat1, lon1, lat2, lon2)
    assert distance > 0
    assert distance < 10  # Devrait être une petite distance


@pytest.mark.utils
def test_calculer_distance_antipodale():
    """Test distance entre deux points diamétralement opposés sur Terre"""
    # Points approximativement opposés
    lat1, lon1 = 0, 0  # Point sur l'équateur
    lat2, lon2 = 0, 180  # Point opposé

    distance = calculer_distance(lat1, lon1, lat2, lon2)
    # La demi-circonférence de la Terre est ~20,000 km
    assert 19000 < distance < 21000


# ============================================================================
# Tests d'intégration
# ============================================================================


@pytest.mark.utils
@pytest.mark.integration
def test_afficher_etablissements_avec_evaluations(client):
    """Test afficher_etablissements avec des évaluations incluses"""
    from app.models import Evaluation

    with client.application.app_context():
        # Créer un établissement avec un flan évalué
        etab = Etablissement(
            nom="Boulangerie Evaluée",
            adresse="1 Rue Eval",
            code_postal="69001",
            ville="Lyon",
            latitude=45.75,
            longitude=4.85,
            id_user=1,
        )
        db.session.add(etab)
        db.session.commit()

        flan = Flan(nom="Flan Noté", prix=3.0, id_etab=etab.id_etab, id_user=1)
        db.session.add(flan)
        db.session.commit()

        # Ajouter une évaluation
        evaluation = Evaluation(
            gout=4,
            texture=4,
            pate=3,
            visuel=5,
            description="Très bon flan!",
            id_flan=flan.id_flan,
            id_user=1,
        )
        db.session.add(evaluation)
        db.session.commit()

        # Tester afficher_etablissements
        result_etab, result_json = afficher_etablissements([etab])

        assert len(result_etab) == 1
        assert result_json[0]["nom"] == "Boulangerie Evaluée"
        assert "flans" in result_json[0]
        assert len(result_json[0]["flans"]) == 1

        # Nettoyage
        db.session.delete(evaluation)
        db.session.delete(flan)
        db.session.delete(etab)
        db.session.commit()
