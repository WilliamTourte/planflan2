"""
Tests pour les fonctions utilitaires (outils.py)
"""

from app.outils import calculer_distance, afficher_etablissements, enlever_accents
from app.models import Etablissement, Flan
from app import db
import pytest

# Importer les fixtures depuis test_securite


@pytest.mark.utils
def test_calculer_distance():
    """Test la fonction calculer_distance avec des coordonnées connues"""
    # Test avec des coordonnées identiques (distance devrait être 0)
    distance = calculer_distance(45.75, 4.85, 45.75, 4.85)
    assert distance == 0.0

    # Test avec des coordonnées proches (Lyon centre vers Lyon Part-Dieu)
    distance = calculer_distance(45.7578, 4.8351, 45.7544, 4.8586)
    assert distance > 0  # Distance positive
    assert distance < 5  # Moins de 5 km

    # Test avec des coordonnées plus éloignées (Lyon vers Paris)
    distance = calculer_distance(45.7578, 4.8351, 48.8566, 2.3522)
    assert distance > 300  # Plus de 300 km
    assert distance < 500  # Moins de 500 km


@pytest.mark.utils
def test_enlever_accents():
    """Test la fonction enlever_accents"""
    # Test avec des accents français
    assert enlever_accents("Café") == "Cafe"
    assert enlever_accents("Hôtel") == "Hotel"
    assert enlever_accents("Été") == "Ete"
    assert enlever_accents("À propos") == "A propos"
    assert enlever_accents("Être ou ne pas être") == "Etre ou ne pas etre"

    # Test avec des caractères spéciaux
    assert enlever_accents("Ça va") == "Ca va"
    assert enlever_accents("Mûr") == "Mur"

    # Test avec du texte sans accents
    assert enlever_accents("Hello World") == "Hello World"
    assert enlever_accents("12345") == "12345"
    assert enlever_accents("") == ""


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


def test_enlever_accents_avec_majuscules():
    """Test enlever_accents avec des majuscules accentuées"""
    assert enlever_accents("École") == "Ecole"
    assert enlever_accents("À Paris") == "A Paris"
    assert enlever_accents("Ça Va") == "Ca Va"


def test_enlever_accents_avec_melange():
    """Test enlever_accents avec un mélange de caractères"""
    texte = "L'été 2025 à Paris: café, hôtel et été!"
    resultat = enlever_accents(texte)
    # Vérifier que les accents sont supprimés (mais pas les apostrophes)
    assert "ete" in resultat
    assert "Paris" in resultat
    assert "cafe" in resultat
    assert "hotel" in resultat


def test_calculer_distance_avec_zero():
    """Test calculer_distance avec des valeurs nulles"""
    distance = calculer_distance(0, 0, 0, 0)
    assert distance == 0.0


def test_calculer_distance_grand_ecart():
    """Test calculer_distance avec un grand écart"""
    # New York vers Tokyo
    distance = calculer_distance(40.7128, -74.0060, 35.6762, 139.6503)
    assert abs(distance - 10850) < 100  # Environ 10 850 km


# Tests pour les fonctions CSRF manquantes
@pytest.mark.utils
def test_verifier_csrf_token_sans_token():
    """Test verifier_csrf_token quand aucun token n'est fourni"""
    from app.outils import verifier_csrf_token
    
    # Simuler une requête sans token CSRF
    with current_app.test_request_context('/', method='GET'):
        resultat, message = verifier_csrf_token()
        assert resultat == True  # Devrait être True quand aucun token n'est requis
        assert message is None


@pytest.mark.utils
def test_verifier_csrf_token_avec_token_valide():
    """Test verifier_csrf_token avec un token valide"""
    from app.outils import verifier_csrf_token
    from flask_wtf.csrf import generate_csrf
    
    # Créer un contexte de requête avec un token CSRF valide
    with current_app.test_request_context('/', method='POST'):
        # Générer un token CSRF valide
        csrf_token = generate_csrf()
        
        # Simuler le token dans l'en-tête
        request.headers['X-CSRFToken'] = csrf_token
        
        resultat, message = verifier_csrf_token()
        assert resultat == True
        assert message is None


@pytest.mark.utils
def test_verifier_csrf_token_avec_token_invalide():
    """Test verifier_csrf_token avec un token invalide"""
    from app.outils import verifier_csrf_token
    
    # Créer un contexte de requête avec un token CSRF invalide
    with current_app.test_request_context('/', method='POST'):
        # Utiliser un token clairement invalide
        request.headers['X-CSRFToken'] = 'token_invalide_12345'
        
        resultat, message = verifier_csrf_token()
        assert resultat == False
        assert message == "Token CSRF invalide"


@pytest.mark.utils
def test_verifier_csrf_ou_renvoyer_erreur_sans_token():
    """Test verifier_csrf_ou_renvoyer_erreur quand aucun token n'est fourni"""
    from app.outils import verifier_csrf_ou_renvoyer_erreur
    
    # Simuler une requête sans token CSRF
    with current_app.test_request_context('/', method='GET'):
        resultat, response = verifier_csrf_ou_renvoyer_erreur()
        assert resultat == True
        assert response is None


@pytest.mark.utils
def test_verifier_csrf_ou_renvoyer_erreur_avec_token_invalide():
    """Test verifier_csrf_ou_renvoyer_erreur avec un token invalide"""
    from app.outils import verifier_csrf_ou_renvoyer_erreur
    
    # Créer un contexte de requête avec un token CSRF invalide
    with current_app.test_request_context('/', method='POST'):
        # Utiliser un token clairement invalide
        request.headers['X-CSRFToken'] = 'token_invalide_12345'
        
        resultat, response = verifier_csrf_ou_renvoyer_erreur()
        assert resultat == False
        assert response is not None
        assert response[1] == 403  # Code d'erreur 403 Forbidden
        
        # Vérifier que la réponse contient un message d'erreur JSON
        assert response[0].is_json
        error_data = response[0].get_json()
        assert 'error' in error_data
        assert error_data['error'] == "Token CSRF invalide"


@pytest.mark.utils
def test_enlever_accents_avec_none():
    """Test enlever_accents avec une valeur None"""
    resultat = enlever_accents(None)
    assert resultat == ""  # Devrait retourner une chaîne vide


@pytest.mark.utils
def test_enlever_accents_avec_nombres():
    """Test enlever_accents avec des nombres et caractères spéciaux"""
    assert enlever_accents("12345") == "12345"
    assert enlever_accents("Prix: 3,50€") == "Prix: 3,50€"
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


@pytest.mark.utils
def test_calculer_distance_avec_valeurs_string():
    """Test calculer_distance avec des valeurs sous forme de chaînes"""
    # La fonction devrait convertir les strings en float
    distance = calculer_distance("45.75", "4.85", "48.85", "2.35")
    assert distance > 0
    assert distance < 500  # Lyon -> Paris
