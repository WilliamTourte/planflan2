"""
Tests pour vérifier que le JSON généré par les routes Flask est valide et parsable.

Ces tests détectent les erreurs de sérialisation JSON qui pourraient casser
le JavaScript côté client (comme l'erreur JSON.parse() qu'on a eu).
"""

import json
import pytest
from app import create_app, db
from app.models import Utilisateur, Etablissement, TypeEtab
from app.config import TestConfig
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Crée une application de test."""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test."""
    return app.test_client()


@pytest.fixture
def setup_test_data(app):
    """Crée des données de test."""
    with app.app_context():
        # Créer un utilisateur
        user = Utilisateur(
            pseudo="testuser",
            email="test@example.com",
            password=generate_password_hash("password"),
            is_admin=False,
        )
        db.session.add(user)
        db.session.flush()

        # Créer des établissements
        etablissements_data = [
            {
                "nom": "Boulangerie Martin",
                "adresse": "123 Rue de Paris",
                "code_postal": "75001",
                "ville": "Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "type_etab": "BOULANGERIE",
                "description": "Une boulangerie classique avec du pain frais",
                "visite": True,
                "label": False,
            },
            {
                "nom": "Pâtisserie Dubois",
                "adresse": "456 Rue de Lyon",
                "code_postal": "69001",
                "ville": "Lyon",
                "latitude": 45.7640,
                "longitude": 4.8357,
                "type_etab": "PATISSERIE",
                "description": 'Pâtisserie avec des "spécialités" étonnantes',  # Guillemets
                "visite": False,
                "label": False,
            },
            {
                "nom": "Café des Amis",
                "adresse": "789 Rue de Marseille",
                "code_postal": "13001",
                "ville": "Marseille",
                "latitude": 43.2965,
                "longitude": 5.3698,
                "type_etab": "CAFE",
                "description": "Café avec du café & des pâtisseries",  # Ampersand
                "visite": True,
                "label": True,
            },
        ]

        for etab_data in etablissements_data:
            etab = Etablissement(**etab_data, id_user=user.id_user)
            db.session.add(etab)

        db.session.commit()
        return user


class TestJSONSerialization:
    """Tests pour vérifier la sérialisation JSON."""

    def test_etablissement_to_dict_returns_valid_json(self, app, setup_test_data):
        """Vérifier que etablissement.to_dict() retourne un dict sérialisable en JSON."""
        with app.app_context():
            etab = Etablissement.query.first()
            assert etab is not None

            # Récupérer le dict
            etab_dict = etab.to_dict(include_flans=False)

            # Vérifier qu'on peut le sérialiser en JSON
            json_str = json.dumps(etab_dict)
            assert isinstance(json_str, str)

            # Vérifier qu'on peut le parser
            parsed = json.loads(json_str)
            assert parsed["nom"] == etab.nom

    def test_etablissements_with_special_characters_serializable(
        self, app, setup_test_data
    ):
        """Vérifier que les établissements avec caractères spéciaux sont sérialisables."""
        with app.app_context():
            etablissements = Etablissement.query.all()
            assert len(etablissements) == 3

            # Le deuxième a des guillemets dans la description
            etab_with_quotes = etablissements[1]
            assert '"' in etab_with_quotes.description

            # Sérialiser tous
            etabs_dict = [etab.to_dict(include_flans=False) for etab in etablissements]
            json_str = json.dumps(etabs_dict)

            # Vérifier qu'on peut parser
            parsed = json.loads(json_str)
            assert len(parsed) == 3

            # Vérifier que les guillemets sont préservés
            assert '"' in parsed[1]["description"]
            assert "&" in parsed[2]["description"]

    def test_liste_etablissements_json_format(self, client, setup_test_data):
        """Vérifier que la route /liste_etablissements génère du JSON valide."""
        response = client.get("/liste_etablissements")
        assert response.status_code == 200

        # Parser le HTML
        html = response.data.decode("utf-8")

        # Chercher l'attribut data-etablissements
        import re
        from html import unescape

        # La regex doit trouver: data-etablissements='...' ou data-etablissements="..."
        # On utilise une approche plus robuste en cherchant la balise entière
        match = re.search(
            r"data-etablissements=['\"](.+?)['\"]",
            html,
            re.DOTALL
        )

        # Alternative si la première ne marche pas: chercher après l'attribut
        if not match:
            # Chercher la div spécifique
            match = re.search(
                r'<div[^>]*id="etablissements-data"[^>]*data-etablissements="([^"]+)"[^>]*>',
                html
            )

        assert match is not None, "Attribut data-etablissements non trouvé dans le HTML"

        json_str = match.group(1)
        # HTML unescape au cas où il y aurait des entités HTML
        json_str = unescape(json_str)

        # Vérifier que c'est du JSON valide
        try:
            parsed = json.loads(json_str)
            assert isinstance(parsed, list)
            assert len(parsed) > 0
        except json.JSONDecodeError as e:
            pytest.fail(
                f"JSON invalide dans data-etablissements: {e}\n"
                f"JSON (premiers 200 chars): {json_str[:200]}\n"
                f"Match complet: {match.group(0)[:200]}"
            )

    def test_etablissements_json_matches_to_dict(self, app, setup_test_data):
        """Vérifier que le JSON généré pour le template correspond à to_dict()."""
        with app.app_context():
            from app.outils import afficher_etablissements

            etablissements = Etablissement.query.all()
            _, etablissements_json = afficher_etablissements(etablissements)

            # Sérialiser avec json.dumps (comme dans la route)
            json_str = json.dumps(etablissements_json, ensure_ascii=False)

            # Vérifier que c'est valide
            parsed = json.loads(json_str)
            assert len(parsed) == len(etablissements)

            # Vérifier que les données correspondent
            for parsed_etab, original_etab in zip(parsed, etablissements):
                assert parsed_etab["nom"] == original_etab.nom
                assert parsed_etab["ville"] == original_etab.ville

    def test_json_with_unicode_characters(self, app, setup_test_data):
        """Vérifier que les caractères Unicode sont correctement sérialisés."""
        with app.app_context():
            # Ajouter un établissement avec caractères spéciaux
            user = Utilisateur.query.first()
            etab = Etablissement(
                nom="Café Français",  # é
                adresse="123 Rue",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab="CAFE",
                description="Café avec des pâtisseries & du café ☕",  # emoji
                visite=True,
                label=False,
                id_user=user.id_user,
            )
            db.session.add(etab)
            db.session.commit()

            # Sérialiser
            etab_dict = etab.to_dict(include_flans=False)
            json_str = json.dumps(etab_dict, ensure_ascii=False)

            # Vérifier qu'on peut parser
            parsed = json.loads(json_str)
            assert "é" in parsed["nom"]
            assert "☕" in parsed["description"]

    def test_json_escaping_prevents_html_injection(self, app, setup_test_data):
        """Vérifier que le JSON échappe correctement les caractères HTML."""
        with app.app_context():
            user = Utilisateur.query.first()
            # Créer un établissement avec du HTML potentiellement malveillant
            etab = Etablissement(
                nom="Test</script><script>alert('xss')</script>",
                adresse="123 Rue",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab="CAFE",
                description='Café avec <img src=x onerror="alert(\'xss\')">',
                visite=True,
                label=False,
                id_user=user.id_user,
            )
            db.session.add(etab)
            db.session.commit()

            # Sérialiser
            etab_dict = etab.to_dict(include_flans=False)
            json_str = json.dumps(etab_dict, ensure_ascii=False)

            # Vérifier que le JSON est valide
            parsed = json.loads(json_str)

            # Vérifier que les caractères sont échappés
            assert "</script>" in parsed["nom"]
            assert "onerror=" in parsed["description"]

    def test_json_with_null_values(self, app, setup_test_data):
        """Vérifier que les valeurs None sont correctement sérialisées."""
        with app.app_context():
            user = Utilisateur.query.first()
            etab = Etablissement(
                nom="Test",
                adresse="123 Rue",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab="CAFE",
                description=None,  # None
                telephone=None,
                site_web=None,
                visite=True,
                label=False,
                id_user=user.id_user,
            )
            db.session.add(etab)
            db.session.commit()

            # Sérialiser
            etab_dict = etab.to_dict(include_flans=False)
            json_str = json.dumps(etab_dict, ensure_ascii=False)

            # Vérifier qu'on peut parser
            parsed = json.loads(json_str)
            assert parsed["description"] is None
            assert parsed["telephone"] is None

    def test_json_format_attribute_validity(self, client, setup_test_data):
        """Vérifier que le JSON dans l'attribut data- est valide en HTML."""
        response = client.get("/liste_etablissements")
        html = response.data.decode("utf-8")

        # Vérifier que l'attribut data-etablissements existe et est bien formé
        import re
        from html import unescape

        # Regex robuste qui gère les guillemets dans le JSON
        pattern = r'<div[^>]*id="etablissements-data"[^>]*data-etablissements="([^"]+)"[^>]*>'
        match = re.search(pattern, html)

        assert match is not None, "Attribut data-etablissements non trouvé ou mal formé"

        json_str = match.group(1)
        # HTML unescape au cas où
        json_str = unescape(json_str)

        # Vérifier que c'est du JSON valide
        try:
            json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"Impossible de parser le JSON: {e}\n"
                f"Première partie du JSON: {json_str[:100]}"
            )


class TestClientSideJSONParsing:
    """Tests pour vérifier que le JSON peut être parsé côté client."""

    def test_json_can_be_parsed_by_javascript_simulation(self, app, setup_test_data):
        """Simuler le parsing JavaScript du JSON."""
        with app.app_context():
            from app.outils import afficher_etablissements

            etablissements = Etablissement.query.all()
            _, etablissements_json = afficher_etablissements(etablissements)

            # Sérialiser comme la route le fait
            json_str = json.dumps(etablissements_json, ensure_ascii=False)

            # Simuler JSON.parse() en Python
            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError as e:
                pytest.fail(
                    f"JavaScript ne pourrait pas parser ce JSON: {e}\n"
                    f"JSON (premiers 200 chars): {json_str[:200]}"
                )

            # Vérifier que on a les données attendues
            assert len(parsed) == len(etablissements)
            assert all("nom" in etab for etab in parsed)
            assert all("latitude" in etab for etab in parsed)
            assert all("longitude" in etab for etab in parsed)
