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
