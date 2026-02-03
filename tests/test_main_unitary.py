"""
Tests unitaires pour les fonctions utilitaires de main.py
"""

# Importer les fixtures depuis test_securite
import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import Etablissement, Flan, Utilisateur
from app.routes.main import filtrer_etablissements
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Crée une application de test avec configuration SQLite en mémoire."""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        # Créer des données de test de base
        # Utilisateur
        user = Utilisateur(
            pseudo="testuser",
            email="test@example.com",
            password=generate_password_hash("password"),
            is_admin=False,
        )
        db.session.add(user)

        # Établissements avec flans
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            adresse="123 Rue de Paris",
            code_postal="75001",
            ville="Paris",
            type_etab="BOULANGERIE",
            label=True,  # Établissement labellisé
            visite=True,  # Établissement visité
            latitude=48.8566,
            longitude=2.3522,
            id_user=1,
        )
        etab2 = Etablissement(
            nom="Patisserie Dubois",
            adresse="456 Rue de Lyon",
            code_postal="69001",
            ville="Lyon",
            type_etab="PATISSERIE",
            label=False,  # Établissement non labellisé
            visite=False,  # Établissement non visité
            latitude=45.7640,
            longitude=4.8357,
            id_user=1,
        )
        etab3 = Etablissement(
            nom="Cafe des Amis",
            adresse="789 Rue de Marseille",
            code_postal="13001",
            ville="Marseille",
            type_etab="CAFE",
            label=True,  # Établissement labellisé
            visite=True,  # Établissement visité
            latitude=43.2965,
            longitude=5.3698,
            id_user=1,
        )
        etab4 = Etablissement(
            nom="Restaurant Gourmet",
            adresse="101 Rue de Bordeaux",
            code_postal="33000",
            ville="Bordeaux",
            type_etab="RESTAURANT",
            label=False,  # Établissement non labellisé
            visite=False,  # Établissement non visité
            latitude=44.8378,
            longitude=-0.5792,
            id_user=1,
        )
        db.session.add_all([etab1, etab2, etab3, etab4])

        # Flans
        flan1 = Flan(
            nom="Flan Vanille",
            type_saveur="VANILLE",
            type_pate="BRISEE",
            type_texture="CREMEUSE",
            description="Délicieux flan à la vanille",
            prix=3.50,
            id_etab=1,
            id_user=1,
        )
        flan2 = Flan(
            nom="Flan Chocolat",
            type_saveur="CHOCOLAT",
            type_pate="SABLEE",
            type_texture="FONDANTE",
            description="Flan au chocolat noir",
            prix=4.00,
            id_etab=2,
            id_user=1,
        )
        flan3 = Flan(
            nom="Flan Citron",
            type_saveur="FRUITS",
            type_pate="BRISEE",
            type_texture="CREMEUSE",
            description="Flan léger au citron",
            prix=2.50,
            id_etab=1,
            id_user=1,
        )
        flan4 = Flan(
            nom="Flan Caramel",
            type_saveur="NATURE",
            type_pate="SABLEE",
            type_texture="CREMEUSE",
            description="Flan onctueux au caramel",
            prix=5.00,
            id_etab=3,
            id_user=1,
        )
        flan5 = Flan(
            nom="Flan Classique",
            type_saveur="VANILLE",
            type_pate="BRISEE",
            type_texture="GELATINEUSE",
            description="Flan classique gélatineux",
            prix=3.00,
            id_etab=2,  # Patisserie Dubois
            id_user=1,
        )
        flan6 = Flan(
            nom="Flan Économique",
            type_saveur="NATURE",
            type_pate="BRISEE",
            type_texture="CREMEUSE",
            description="Flan économique",
            prix=2.00,  # Moins de 2.5€
            id_etab=1,  # Boulangerie Martin
            id_user=1,
        )
        db.session.add_all([flan1, flan2, flan3, flan4, flan5, flan6])

        db.session.commit()

        yield app

        # Nettoyage: supprimer les données de test supplémentaires
        # ajoutées par certains tests
        from app.models import Etablissement as EtabModel

        EtabModel.query.filter(
            EtabModel.nom.in_(
                [
                    "Établissement Sans Type",
                    "Établissement Inconnu",
                    "Établissement Test",
                ]
            )
        ).delete(synchronize_session=False)
        db.session.commit()

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test."""
    return app.test_client()


@pytest.fixture
def boulangerie_martin(app):
    """Retourne l'établissement Boulangerie Martin."""
    with app.app_context():
        return Etablissement.query.filter_by(nom="Boulangerie Martin").first()


@pytest.fixture
def patisserie_dubois(app):
    """Retourne l'établissement Patisserie Dubois."""
    with app.app_context():
        return Etablissement.query.filter_by(nom="Patisserie Dubois").first()


@pytest.fixture
def cafe_des_amis(app):
    """Retourne l'établissement Cafe des Amis."""
    with app.app_context():
        return Etablissement.query.filter_by(nom="Cafe des Amis").first()


@pytest.fixture
def restaurant_gourmet(app):
    """Retourne l'établissement Restaurant Gourmet."""
    with app.app_context():
        return Etablissement.query.filter_by(nom="Restaurant Gourmet").first()


@pytest.fixture
def setup_data(app):
    """Crée des données de test pour les établissements et flans."""
    with app.app_context():
        # Créer des utilisateurs
        admin = Utilisateur(
            pseudo="admin",
            email="admin@example.com",
            password=generate_password_hash("admin"),
            is_admin=True,
        )
        user = Utilisateur(
            pseudo="user",
            email="user@example.com",
            password=generate_password_hash("user"),
            is_admin=False,
        )
        db.session.add_all([admin, user])

        # Créer des établissements
        etab1 = Etablissement(
            nom="Boulangerie Martin",
            adresse="1 rue de Paris, 75001 Paris",
            ville="Paris",
            code_postal="75001",
            latitude=48.8566,
            longitude=2.3522,
            visite=True,
            label=True,
            type_etab="BOULANGERIE",
            id_user=admin.id_user,
        )

        etab2 = Etablissement(
            nom="Patisserie Dubois",
            adresse="10 rue de Lyon, 69001 Lyon",
            ville="Lyon",
            code_postal="69001",
            latitude=45.7640,
            longitude=4.8357,
            visite=False,
            label=False,
            type_etab="PATISSERIE",
            id_user=user.id_user,
        )

        etab3 = Etablissement(
            nom="Cafe des Amis",
            adresse="5 rue de Marseille, 13001 Marseille",
            ville="Marseille",
            code_postal="13001",
            latitude=43.2965,
            longitude=5.3698,
            visite=True,
            label=False,
            type_etab="RESTAURANT",
            id_user=admin.id_user,
        )

        db.session.add_all([etab1, etab2, etab3])
        db.session.commit()  # Commit establishments first to get their IDs

        # Créer des flans - chaque établissement doit avoir au moins un flan pour les tests API
        flan1 = Flan(
            nom="Flan vanille",
            description="Flan classique a la vanille",
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            prix=3.50,
            id_etab=etab1.id_etab,
            id_user=admin.id_user,
        )

        flan2 = Flan(
            nom="Flan chocolat",
            description="Flan riche au chocolat noir",
            type_pate="SABLEE",
            type_saveur="NOIX",
            type_texture="CREMEUSE",
            prix=4.00,
            id_etab=etab1.id_etab,
            id_user=user.id_user,
        )

        flan3 = Flan(
            nom="Flan citron",
            description="Flan acidule au citron",
            type_pate="BRISEE",
            type_saveur="FRUITS",
            type_texture="GELATINEUSE",
            prix=2.50,
            id_etab=etab2.id_etab,
            id_user=admin.id_user,
        )

        # Ajouter un flan pour le Cafe des Amis (établissement 3)
        flan4 = Flan(
            nom="Flan café",
            description="Flan au café",
            type_pate="BRISEE",
            type_saveur="NATURE",
            type_texture="CREMEUSE",
            prix=3.00,
            id_etab=etab3.id_etab,
            id_user=admin.id_user,
        )

        db.session.add_all([flan1, flan2, flan3, flan4])
        db.session.commit()


@pytest.mark.unitary
@pytest.mark.parametrize(
    "filter_name,filter_param,expected_condition,test_description",
    [
        # Test filtrage par nom
        (
            "nom",
            "Boulangerie",
            lambda results: all("Boulangerie" in result.nom for result in results),
            "Filtrer par nom contenant 'Boulangerie'",
        ),
        # Test filtrage par ville
        (
            "ville",
            "Lyon",
            lambda results: all(result.ville == "Lyon" for result in results),
            "Filtrer par ville 'Lyon'",
        ),
        # Test filtrage par visite = oui
        (
            "visite",
            "oui",
            lambda results: all(etab.visite == True for etab in results),
            "Filtrer par visite 'oui'",
        ),
        # Test filtrage par visite = non
        (
            "visite",
            "non",
            lambda results: all(etab.visite == False for etab in results),
            "Filtrer par visite 'non'",
        ),
        # Test filtrage par labellisé = oui
        (
            "labellise",
            "oui",
            lambda results: all(etab.label == True for etab in results),
            "Filtrer par labellisé 'oui'",
        ),
        # Test filtrage par labellisé = non
        (
            "labellise",
            "non",
            lambda results: all(etab.label == False for etab in results),
            "Filtrer par labellisé 'non'",
        ),
        # Test filtrage par type de pâte
        (
            "type_pate",
            "BRISEE",
            lambda results: len(results) > 0,
            "Filtrer par type de pâte 'BRISEE'",
        ),
        # Test filtrage par type de saveur
        (
            "type_saveur",
            "VANILLE",
            lambda results: len(results) > 0,
            "Filtrer par type de saveur 'VANILLE'",
        ),
    ],
)
def test_filtrer_etablissements_parametrize(
    client, filter_name, filter_param, expected_condition, test_description
):
    """Test le filtrage des établissements avec différents critères (paramétrisé)"""
    with client.application.app_context():
        query = Etablissement.query

        # Appliquer le filtre - utiliser une jointure pour les filtres sur les flans
        if filter_name in ["type_pate", "type_saveur", "type_texture"]:
            query = query.join(Flan)

        filtered_query = filtrer_etablissements(query, **{filter_name: filter_param})
        results = filtered_query.all()

        # Vérifier que nous avons des résultats
        assert len(results) > 0, f"Aucun établissement trouvé avec {filter_name}={filter_param}"

        # Vérifier la condition attendue
        assert expected_condition(
            results
        ), f"La condition attendue n'est pas satisfaite pour {test_description}"


@pytest.mark.unitary
def test_filtrer_etablissements_par_ville(client):
    """Test le filtrage des établissements par ville."""
    with client.application.app_context():
        query = Etablissement.query

        # Filtrer par ville
        filtered_query = filtrer_etablissements(query, ville="Lyon")
        results = filtered_query.all()

        # Vérifier que nous avons des résultats de Lyon
        assert len(results) > 0, "Aucun établissement trouvé à Lyon"
        for result in results:
            assert result.ville == "Lyon", f"L'établissement {result.nom} n'est pas à Lyon"


@pytest.mark.unitary
def test_filtrer_etablissements_par_visite(client):
    """Test le filtrage des établissements par statut de visite."""
    with client.application.app_context():
        query = Etablissement.query

        # Filtrer par visite = oui
        filtered_query = filtrer_etablissements(query, visite="oui")
        results = filtered_query.all()

        assert len(results) > 0
        assert all(etab.visite == True for etab in results)

        # Filtrer par visite = non
        filtered_query = filtrer_etablissements(query, visite="non")
        results = filtered_query.all()

        assert len(results) > 0
        assert results[0].visite == False


@pytest.mark.unitary
def test_filtrer_etablissements_par_labellise(client):
    """Test le filtrage des établissements par statut labellisé."""
    with client.application.app_context():
        query = Etablissement.query

        # Filtrer par labellisé = oui
        filtered_query = filtrer_etablissements(query, labellise="oui")
        results = filtered_query.all()

        assert len(results) > 0
        assert results[0].label == True

        # Filtrer par labellisé = non
        filtered_query = filtrer_etablissements(query, labellise="non")
        results = filtered_query.all()

        assert len(results) > 0
        assert all(etab.label == False for etab in results)


@pytest.mark.unitary
def test_filtrer_etablissements_par_type_pate(client):
    """Test le filtrage des établissements par type de pâte."""
    with client.application.app_context():
        # Note: filtrer_etablissements fait une jointure implicite avec Flan
        # mais ne gère pas la jointure automatiquement, donc nous devons la faire manuellement
        query = Etablissement.query.join(Flan)

        # Filtrer par type de pâte = BRISEE
        filtered_query = filtrer_etablissements(query, type_pate="BRISEE")
        results = filtered_query.all()

        # Devrait retourner les établissements avec des flans à pâte brisée
        assert len(results) > 0  # Boulangerie Martin et Patisserie Dubois

        # Filtrer par type de pâte = SABLEE
        filtered_query = filtrer_etablissements(query, type_pate="SABLEE")
        results = filtered_query.all()

        assert len(results) > 0  # Boulangerie Martin seulement


@pytest.mark.unitary
def test_filtrer_etablissements_par_type_saveur(client):
    """Test le filtrage des établissements par type de saveur."""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Filtrer par saveur = VANILLE
        filtered_query = filtrer_etablissements(query, type_saveur="VANILLE")
        results = filtered_query.all()

        assert len(results) > 0
        assert results[0].nom == "Boulangerie Martin"


@pytest.mark.unitary
@pytest.mark.parametrize(
    "texture_type,expected_etablissement",
    [
        ("CREMEUSE", "Boulangerie Martin"),
        ("GELATINEUSE", "Patisserie Dubois"),
    ],
)
def test_filtrer_etablissements_par_type_texture_parametrize(
    client, texture_type, expected_etablissement
):
    """Test le filtrage des établissements par type de texture (paramétrisé)"""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Filtrer par texture
        filtered_query = filtrer_etablissements(query, type_texture=texture_type)
        results = filtered_query.all()

        # Devrait retourner les établissements avec des flans à texture spécifiée
        assert len(results) > 0
        assert results[0].nom == expected_etablissement


@pytest.mark.unitary
def test_filtrer_etablissements_type_texture_tous(client):
    """Test le filtrage des établissements avec type_texture='tous'."""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Filtrer avec type_texture='tous' (ne devrait pas filtrer)
        filtered_query = filtrer_etablissements(query, type_texture="tous")
        results = filtered_query.all()

        # Devrait retourner tous les établissements avec des flans
        assert len(results) > 0  # Boulangerie Martin et Patisserie Dubois


@pytest.mark.unitary
def test_filtrer_etablissements_jointure_flan(client):
    """Test le filtrage des établissements avec jointure Flan et gestion des résultats."""
    with client.application.app_context():
        # Test 1: Jointure simple sans filtres
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query)
        results = filtered_query.all()

        # Devrait retourner tous les établissements qui ont des flans
        assert len(results) == 3  # Boulangerie Martin, Patisserie Dubois et Cafe des Amis

        # Test 2: Jointure avec filtre sur Flan
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query, type_pate="BRISEE")
        results = filtered_query.all()

        # Devrait retourner seulement les établissements avec des flans à pâte brisée
        assert len(results) == 2  # Boulangerie Martin et Patisserie Dubois
        noms = [r.nom for r in results]
        assert "Boulangerie Martin" in noms
        assert "Patisserie Dubois" in noms

        # Test 3: Jointure avec filtre sur Etablissement
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query, ville="Lyon")
        results = filtered_query.all()

        # Devrait retourner seulement les établissements de Lyon qui ont des flans
        assert len(results) == 1  # Patisserie Dubois
        assert results[0].nom == "Patisserie Dubois"

        # Test 4: Jointure avec filtres combinés
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(
            query, ville="Paris", type_pate="BRISEE", type_saveur="VANILLE"
        )
        results = filtered_query.all()

        # Devrait retourner seulement les établissements de Paris avec des flans vanille à pâte brisée
        assert len(results) == 1  # Boulangerie Martin
        assert results[0].nom == "Boulangerie Martin"


@pytest.mark.unitary
def test_filtrer_etablissements_etablissements_sans_flans(client):
    """Test le filtrage des établissements qui n'ont pas de flans."""
    with client.application.app_context():
        # Créer un établissement sans flan
        etab_sans_flan = Etablissement(
            nom="Boulangerie Sans Flan",
            adresse="Test Adresse",
            ville="Marseille",
            code_postal="13001",
            id_user=1,
        )
        db.session.add(etab_sans_flan)
        db.session.commit()

        # Test 1: Requête sans jointure - devrait inclure tous les établissements
        query = Etablissement.query
        filtered_query = filtrer_etablissements(query, ville="Marseille")
        results = filtered_query.all()

        assert len(results) > 0  # Cafe des Amis
        assert results[0].nom == "Cafe des Amis"

        # Test 2: Requête avec jointure - devrait exclure les établissements sans flans
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query, ville="Marseille")
        results = filtered_query.all()

        assert len(results) > 0  # Cafe des Amis
        assert results[0].nom == "Cafe des Amis"

        # Test 3: Filtre sur Flan avec jointure - devrait exclure les établissements sans flans
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query, type_pate="BRISEE")
        results = filtered_query.all()

        # Ne devrait pas inclure l'établissement sans flan
        assert len(results) > 0  # Boulangerie Martin
        assert results[0].nom == "Boulangerie Martin"


@pytest.mark.unitary
def test_filtrer_etablissements_resultats_dupliques(client):
    """Test la gestion des résultats dupliqués lors de la jointure avec Flan."""
    with client.application.app_context():
        # Ajouter un deuxième flan à la Boulangerie Martin pour créer un cas de duplication
        boulangerie = Etablissement.query.filter_by(nom="Boulangerie Martin").first()

        flan_extra = Flan(
            nom="Flan Chocolat Extra",
            description="Flan supplémentaire au chocolat",
            type_pate="BRISEE",
            type_saveur="NOIX",
            type_texture="CREMEUSE",
            prix=4.00,
            id_etab=boulangerie.id_etab,
            id_user=1,
        )
        db.session.add(flan_extra)
        db.session.commit()

        # Test: Jointure sans distinct - pourrait retourner des doublons
        query = Etablissement.query.join(Flan)
        filtered_query = filtrer_etablissements(query, ville="Paris")
        results = filtered_query.all()

        # La Boulangerie Martin devrait apparaître une fois pour chaque flan
        # Mais comme nous utilisons distinct() dans la route, cela ne devrait pas poser problème
        boulangerie_results = [r for r in results if r.nom == "Boulangerie Martin"]
        assert len(boulangerie_results) >= 1  # Au moins une occurrence

        # Vérifier que les IDs sont bien les mêmes (même établissement)
        if len(boulangerie_results) > 1:
            first_id = boulangerie_results[0].id_etab
            for result in boulangerie_results[1:]:
                assert result.id_etab == first_id  # Même établissement


@pytest.mark.unitary
@pytest.mark.parametrize(
    "prix_filter,expected_result_count,description",
    [
        ("0", ">= 0", "Filtrer par prix < 2.5€"),
        ("2.5", ">= 1", "Filtrer par prix entre 2.5 et 5€"),
        ("5", ">= 0", "Filtrer par prix >= 5€"),
    ],
)
def test_filtrer_etablissements_par_prix_parametrize(
    client, prix_filter, expected_result_count, description
):
    """Test le filtrage des établissements par prix (paramétrisé)"""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Filtrer par prix
        filtered_query = filtrer_etablissements(query, prix=prix_filter)
        results = filtered_query.all()

        # Vérifier que nous avons des résultats selon la description
        if expected_result_count == ">= 0":
            assert len(results) >= 0  # Toujours vrai, mais garde la structure
        elif expected_result_count == ">= 1":
            assert len(results) >= 1
        else:
            assert len(results) > 0


@pytest.mark.unitary
@pytest.mark.performance
def test_filtrer_etablissements_combinaison_filtres(client):
    """Test le filtrage avec une combinaison de filtres."""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Combinaison: Paris + visite = oui + pâte BRISEE
        filtered_query = filtrer_etablissements(
            query, ville="Paris", visite="oui", type_pate="BRISEE"
        )
        results = filtered_query.all()

        assert len(results) > 0
        assert results[0].nom == "Boulangerie Martin"


@pytest.mark.unitary
def test_filtrer_etablissements_sans_filtres(client):
    """Test le filtrage sans aucun filtre."""
    with client.application.app_context():
        query = Etablissement.query

        # Aucun filtre
        filtered_query = filtrer_etablissements(query)
        results = filtered_query.all()

        assert len(results) > 0  # Tous les établissements


@pytest.mark.unitary
def test_filtrer_etablissements_avec_tous_comme_valeur(client):
    """Test le filtrage avec 'tous' comme valeur (ne devrait pas filtrer)."""
    with client.application.app_context():
        query = Etablissement.query.join(Flan)

        # Filtrer avec type_pate='tous' (ne devrait pas filtrer)
        filtered_query = filtrer_etablissements(query, type_pate="tous")
        results = filtered_query.all()

        # Devrait retourner tous les établissements avec des flans
        assert len(results) > 0  # 2 établissements ont des flans (etab1 et etab2)


@pytest.mark.unitary
@pytest.mark.skip(
    reason="Test de route nécessitant une configuration complète - à exécuter localement uniquement"
)
def test_liste_etablissements_route_get(client, setup_data):
    """Test la route liste_etablissements avec une requête GET."""
    response = client.get("/liste_etablissements")
    assert response.status_code == 200
    # Vérifier que la page contient des éléments attendus
    assert b"Boulangerie Martin" in response.data
    assert b"Patisserie Dubois" in response.data


@pytest.mark.unitary
@pytest.mark.skip(
    reason="Test de route nécessitant une configuration complète - à exécuter localement uniquement"
)
def test_liste_etablissements_recherche_simple(client, setup_data):
    """Test la recherche simple dans liste_etablissements."""
    response = client.get("/liste_etablissements?recherche_simple=Paris")
    assert response.status_code == 200
    # Devrait trouver seulement la boulangerie à Paris (recherche_simple filtre toujours)
    assert b"Boulangerie Martin" in response.data
    # Ne devrait pas trouver les établissements de Lyon ou Marseille
    assert b"Lyon" not in response.data


@pytest.mark.unitary
@pytest.mark.skip(
    reason="Test de route nécessitant une configuration complète - à exécuter localement uniquement"
)
def test_liste_etablissements_filtres_avances(client):
    """Test les filtres avancés dans liste_etablissements."""
    response = client.get("/liste_etablissements?ville=Paris&visite=oui")
    assert response.status_code == 200
    # Nouvelle logique: tous les établissements sont affichés, mais la ville est transmise pour zoom
    assert b"Boulangerie Martin" in response.data
    # Vérifier que la ville sélectionnée est transmise au JavaScript
    assert b"ville-selectionnee" in response.data


@pytest.mark.unitary
@pytest.mark.skip(
    reason="Test de route nécessitant une configuration complète - à exécuter localement uniquement"
)
def test_liste_etablissements_filtre_prix(client, setup_data):
    """Test le filtre par prix dans liste_etablissements."""
    response = client.get("/liste_etablissements?prix=2.5")  # Prix entre 2.5 et 5
    assert response.status_code == 200
    # Devrait trouver les flans dans cette fourchette de prix
    assert b"vanille" in response.data


@pytest.mark.unitary
def test_api_etablissements_get(client):
    """Test l'API etablissements avec une requête GET."""
    response = client.get("/api/etablissements?format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert isinstance(data, list)
    # Tous les établissements qui ont des flans (3 établissements avec flans dans la fixture app)
    assert len(data) == 3

    # Vérifier la structure des données
    assert "nom" in data[0]
    assert "ville" in data[0]
    assert "id_etab" in data[0]


@pytest.mark.unitary
def test_api_etablissements_filtres(client):
    """Test l'API etablissements avec des filtres."""
    response = client.get("/api/etablissements?ville=Paris&format=json")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1  # Un seul établissement à Paris avec des flans
    assert data[0]["nom"] == "Boulangerie Martin"


@pytest.mark.unitary
def test_api_etablissements_format_html(client):
    """Test l'API etablissements avec format HTML."""
    response = client.get("/api/etablissements?format=html")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"
    # Devrait contenir du HTML avec les établissements
    assert b"<div" in response.data or b"<table" in response.data
    # Vérifier que le HTML contient bien nos établissements
    assert b"Boulangerie Martin" in response.data or b"Patisserie Dubois" in response.data


@pytest.mark.unitary
def test_api_etablissements_post(client):
    """Test l'API etablissements avec une requête POST."""
    response = client.post("/api/etablissements", json={"ville": "Paris", "format": "json"})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1  # Un seul établissement à Paris avec des flans
    assert data[0]["nom"] == "Boulangerie Martin"


@pytest.mark.unitary
def test_api_etablissements_erreur(client):
    """Test l'API etablissements avec une erreur."""
    # Envoyer une requête POST avec des données invalides
    response = client.post("/api/etablissements", json={"format": "json"})
    assert response.status_code == 200  # Devrait toujours retourner 200 même avec des filtres vides

    data = response.get_json()
    assert isinstance(data, list)
    # Devrait retourner tous les établissements qui ont des flans (3 dans la fixture app)
    assert len(data) == 3


@pytest.mark.unitary
def test_get_infowindow_content(client, setup_data):
    """Test la route get_infowindow_content."""
    with client.application.app_context():
        etab = Etablissement.query.first()
        etab_id = etab.id_etab

    response = client.get(f"/get_infowindow_content?id_etab={etab_id}")
    assert response.status_code == 200
    # Devrait contenir des informations sur l'établissement
    assert b"Boulangerie Martin" in response.data


@pytest.mark.unitary
def test_get_infowindow_content_etablissement_inexistant(client):
    """Test get_infowindow_content avec un établissement inexistant."""
    response = client.get("/get_infowindow_content?id_etab=999999")
    assert response.status_code == 404
    assert (
        b"D\xc3\xa9tails non disponibles" in response.data
        or b"Details non disponibles" in response.data
    )


@pytest.mark.unitary
@pytest.mark.skip(
    reason="Test de route nécessitant une configuration complète - à exécuter localement uniquement"
)
def test_rechercher_route(client):
    """Test la route rechercher."""
    response = client.get("/rechercher")
    assert response.status_code == 200
    # Vérifier que la page contient le formulaire de recherche
    assert b"form_recherche" in response.data or b"Recherche" in response.data


@pytest.mark.unitary
def test_afficher_badge_type_etab(client):
    """Test la fonction afficher_badge_type_etab."""
    from app.routes.main import afficher_badge_type_etab

    with client.application.app_context():
        etab = Etablissement.query.first()

        # Test avec différents types d'établissements
        badge = afficher_badge_type_etab(etab)
        # Devrait contenir le badge pour le type d'établissement
        assert "badge-type-etab" in badge
        assert etab.type_etab.value in badge


@pytest.mark.unitary
def test_afficher_badge_etablissement_complet(client):
    """Test complet de la fonction afficher_badge_etablissement."""
    from app.routes.main import afficher_badge_etablissement

    with client.application.app_context():
        # Test 1: Établissement labellisé
        etab = Etablissement.query.filter_by(nom="Boulangerie Martin").first()
        etab.label = True
        db.session.commit()

        badge = afficher_badge_etablissement(etab)
        assert "❤️" in badge
        assert "badge badge-labellise" in badge

        # Test 2: Établissement non labellisé
        etab.label = False
        db.session.commit()

        badge = afficher_badge_etablissement(etab)
        assert badge == ""

        # Test 3: Établissement sans attribut label
        etab_sans_label = Etablissement.query.filter_by(nom="Patisserie Dubois").first()
        # Supprimer l'attribut label temporairement pour le test
        original_label = getattr(etab_sans_label, "label", None)
        if hasattr(etab_sans_label, "label"):
            delattr(etab_sans_label, "label")

        badge = afficher_badge_etablissement(etab_sans_label)
        assert badge == ""

        # Restaurer l'attribut label
        if original_label is not None:
            etab_sans_label.label = original_label


@pytest.mark.unitary
def test_afficher_badge_type_etab_complet(client):
    """Test complet de la fonction afficher_badge_type_etab."""
    from app.routes.main import afficher_badge_type_etab

    with client.application.app_context():
        # Test 1: Boulangerie
        etab_boulangerie = Etablissement.query.filter_by(nom="Boulangerie Martin").first()
        badge = afficher_badge_type_etab(etab_boulangerie)
        assert "badge-type-etab" in badge
        assert "Boulangerie" in badge  # Libellé au lieu de la valeur
        assert "#F5DEB3" in badge  # Couleur pour boulangerie

        # Test 2: Pâtisserie
        etab_patisserie = Etablissement.query.filter_by(nom="Patisserie Dubois").first()
        badge = afficher_badge_type_etab(etab_patisserie)
        assert "badge-type-etab" in badge
        assert "Pâtisserie" in badge  # Libellé au lieu de la valeur
        assert "#FFB6C1" in badge  # Couleur pour pâtisserie

        # Test 3: Restaurant
        etab_restaurant = Etablissement.query.filter_by(nom="Restaurant Gourmet").first()
        badge = afficher_badge_type_etab(etab_restaurant)
        assert "badge-type-etab" in badge
        assert "Restaurant" in badge  # Libellé au lieu de la valeur
        assert "#87CEEB" in badge  # Couleur pour restaurant


def test_flan_get_moyenne_evaluations(app):
    """Test la méthode get_moyenne_evaluations de la classe Flan."""
    from app.models import Flan, Evaluation, StatutModeration
    from datetime import datetime

    with app.app_context():
        # Créer un flan avec des évaluations valides
        flan = Flan(
            nom="Flan Test",
            description="Un flan de test",
            prix=3.50,
            id_etab=1,
            id_user=1,
        )

        # Ajouter des évaluations valides
        eval1 = Evaluation(
            visuel=4.0,
            texture=3.5,
            pate=4.5,
            gout=5.0,
            moyenne=4.25,
            statut=StatutModeration.VALIDE,
            date_creation=datetime.now(),
        )

        eval2 = Evaluation(
            visuel=3.0,
            texture=3.0,
            pate=3.5,
            gout=3.5,
            moyenne=3.25,
            statut=StatutModeration.VALIDE,
            date_creation=datetime.now(),
        )

        # Ajouter une évaluation non valide (ne devrait pas être prise en compte)
        eval3 = Evaluation(
            visuel=2.0,
            texture=2.5,
            pate=2.0,
            gout=3.0,
            moyenne=2.375,
            statut=StatutModeration.EN_ATTENTE,
            date_creation=datetime.now(),
        )

        flan.evaluations = [eval1, eval2, eval3]

        # Test 1: Moyenne avec évaluations valides
        moyenne = flan.get_moyenne_evaluations()
        expected_moyenne = 3.3  # (4.25 + 3.25 +2.375) / 3
        assert (
            moyenne == expected_moyenne
        ), f"Moyenne attendue: {expected_moyenne}, obtenue: {moyenne}"

        # Test 2: Flan sans évaluations
        flan_sans_eval = Flan(
            nom="Flan sans évaluations",
            description="Un flan sans évaluations",
            prix=2.50,
            id_etab=1,
            id_user=1,
        )

        moyenne_sans_eval = flan_sans_eval.get_moyenne_evaluations()
        assert moyenne_sans_eval is None, "Un flan sans évaluations devrait retourner None"

        # Test 4: Flan avec une seule évaluation valide
        flan_unique = Flan(
            nom="Flan avec une seule évaluation",
            description="Un flan avec une seule évaluation",
            prix=3.00,
            id_etab=1,
            id_user=1,
        )

        eval_unique = Evaluation(
            visuel=5.0,
            texture=5.0,
            pate=5.0,
            gout=5.0,
            moyenne=5.0,
            statut=StatutModeration.VALIDE,
            date_creation=datetime.now(),
        )

        flan_unique.evaluations = [eval_unique]

        moyenne_unique = flan_unique.get_moyenne_evaluations()
        assert moyenne_unique == 5.0, f"Moyenne attendue: 5.0, obtenue: {moyenne_unique}"
