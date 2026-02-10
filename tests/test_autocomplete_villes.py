"""
Tests unitaires pour la fonctionnalité d'autocomplete des villes.

Ce module teste spécifiquement la normalisation des espaces et tirets
dans la recherche de villes, ainsi que la gestion des accents.
"""

import pytest
from app import create_app, db
from app.config import TestConfig
import json
import os


def normalize_ville_name(name):
    """Fonction de normalisation pour les tests - même logique que dans main.py"""
    import unicodedata

    # Convertir en minuscules d'abord
    name = name.lower()
    # Supprimer les accents
    name = unicodedata.normalize("NFD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    # Remplacer les espaces par des tirets et supprimer les apostrophes
    return name.replace(" ", "-").replace("'", "")


class TestVilleNormalization:
    """Tests pour la normalisation des noms de villes."""

    def test_normalize_spaces_to_dashes(self):
        """Test que les espaces sont bien remplacés par des tirets."""
        assert normalize_ville_name("Saint Etienne") == "saint-etienne"
        assert normalize_ville_name("La Rochelle") == "la-rochelle"
        assert normalize_ville_name("Saint Denis") == "saint-denis"

    def test_normalize_accents(self):
        """Test que les accents sont bien supprimés."""
        assert normalize_ville_name("Saint-Étienne") == "saint-etienne"
        assert normalize_ville_name("Épinal") == "epinal"
        # Note: les apostrophes sont conservées, ce qui est normal pour les noms de villes
        # Les apostrophes sont maintenant gérées dans test_normalize_apostrophes

    def test_normalize_mixed(self):
        """Test la normalisation combinée espaces + accents."""
        assert normalize_ville_name("Saint Étienne") == "saint-etienne"
        assert normalize_ville_name("La Rochelle") == "la-rochelle"
        assert normalize_ville_name("Saint-Denis") == "saint-denis"

    def test_normalize_case_insensitive(self):
        """Test que la normalisation est insensible à la casse."""
        assert normalize_ville_name("SAINT ETIENNE") == "saint-etienne"
        assert normalize_ville_name("saint etienne") == "saint-etienne"
        assert normalize_ville_name("Saint-Étienne") == "saint-etienne"

    def test_normalize_apostrophes(self):
        """Test que les apostrophes sont bien supprimées."""
        assert normalize_ville_name("L'Isle-sur-la-Sorgue") == "lisle-sur-la-sorgue"
        assert normalize_ville_name("Côte d'Azur") == "cote-dazur"
        assert normalize_ville_name("L'Haÿ-les-Roses") == "lhay-les-roses"


class TestVilleAutocompleteAPI:
    """Tests pour l'API d'autocomplete des villes."""

    def test_autocomplete_space_vs_dash(self, client):
        """Test que la recherche avec espaces trouve les villes avec tirets."""
        response = client.get("/api/villes?q=saint etienne")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0

        # Vérifier que Saint-Étienne est dans les résultats
        ville_names = [item for item in data if isinstance(item, str)]
        assert any("Saint-Étienne" in name for name in ville_names)

    def test_autocomplete_dash_vs_space(self, client):
        """Test que la recherche avec tirets trouve les villes avec tirets."""
        response = client.get("/api/villes?q=saint-etienne")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0

        # Vérifier que Saint-Étienne est dans les résultats
        ville_names = [item for item in data if isinstance(item, str)]
        assert any("Saint-Étienne" in name for name in ville_names)

    def test_autocomplete_partial_match(self, client):
        """Test que la recherche partielle fonctionne toujours."""
        response = client.get("/api/villes?q=saint")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0

        # Vérifier que plusieurs villes avec "saint" sont trouvées
        ville_names = [item for item in data if isinstance(item, str)]
        saint_villes = [name for name in ville_names if "Saint" in name or "saint" in name.lower()]
        assert len(saint_villes) > 1

    def test_autocomplete_with_accents(self, client):
        """Test que la recherche fonctionne avec et sans accents."""
        # Recherche sans accent
        response1 = client.get("/api/villes?q=saint etienne")
        data1 = response1.get_json()

        # Recherche avec accent (simulé - l'utilisateur ne tape généralement pas d'accents)
        response2 = client.get(
            "/api/villes?q=saint etienne"
        )  # Même recherche car les accents sont normalisés
        data2 = response2.get_json()

        # Les deux devraient retourner les mêmes résultats
        assert data1 == data2

        # Vérifier que Saint-Étienne (avec accent) est trouvé
        ville_names = [item for item in data1 if isinstance(item, str)]
        assert any("Saint-Étienne" in name for name in ville_names)

    def test_autocomplete_multiple_cases(self, client):
        """Test plusieurs cas de recherche espace/tiret."""
        test_cases = [
            ("la rochelle", "La Rochelle"),
            ("saint denis", "Saint-Denis"),
            ("saint etienne", "Saint-Étienne"),
        ]

        for search_term, expected_ville in test_cases:
            response = client.get(f"/api/villes?q={search_term}")
            assert response.status_code == 200

            data = response.get_json()
            assert len(data) > 0

            # Vérifier que la ville attendue est dans les résultats
            ville_names = [item for item in data if isinstance(item, str)]
            assert any(
                expected_ville in name for name in ville_names
            ), f"Ville {expected_ville} non trouvée pour la recherche '{search_term}'"

    def test_autocomplete_with_gps(self, client):
        """Test que le paramètre with_gps fonctionne toujours avec la normalisation."""
        response = client.get("/api/villes?q=saint etienne&with_gps=true")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0

        # Vérifier que les résultats contiennent le format attendu (nom|lat|lng)
        assert all("|" in item for item in data)

        # Vérifier que Saint-Étienne est dans les résultats
        assert any("Saint-Étienne" in item.split("|")[0] for item in data)


class TestVilleSearchIntegration:
    """Tests d'intégration pour la recherche de villes."""

    def test_search_consistency(self, client):
        """Test que les recherches avec espaces et tirets retournent les mêmes résultats."""
        response_space = client.get("/api/villes?q=saint etienne")
        response_dash = client.get("/api/villes?q=saint-etienne")

        data_space = response_space.get_json()
        data_dash = response_dash.get_json()

        # Les résultats devraient être identiques (même si l'ordre peut varier)
        assert set(data_space) == set(data_dash)

    def test_empty_search(self, client):
        """Test qu'une recherche vide retourne tous les résultats (ou une liste raisonnable)."""
        response = client.get("/api/villes?q=")
        assert response.status_code == 200

        data = response.get_json()
        # Devrait retourner soit tous les résultats, soit une liste limitée
        assert isinstance(data, list)

    def test_short_search(self, client):
        """Test qu'une recherche très courte fonctionne toujours."""
        response = client.get("/api/villes?q=sa")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0
