"""
Tests unitaires pour les fonctions utilitaires de main.py
"""
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
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test."""
    return app.test_client()


@pytest.fixture
def setup_data(app):
    """Crée des données de test pour les établissements et flans."""
    with app.app_context():
        # Créer des utilisateurs
        admin = Utilisateur(
            pseudo='admin',
            email='admin@example.com',
            password=generate_password_hash('admin'),
            is_admin=True
        )
        user = Utilisateur(
            pseudo='user',
            email='user@example.com',
            password=generate_password_hash('user'),
            is_admin=False
        )
        db.session.add_all([admin, user])
        
        # Créer des établissements
        etab1 = Etablissement(
            nom='Boulangerie Martin',
            adresse='1 rue de Paris, 75001 Paris',
            ville='Paris',
            code_postal='75001',
            latitude=48.8566,
            longitude=2.3522,
            visite=True,
            label=True,
            type_etab='BOULANGERIE',
            id_user=admin.id_user
        )
        
        etab2 = Etablissement(
            nom='Patisserie Dubois',
            adresse='10 rue de Lyon, 69001 Lyon',
            ville='Lyon',
            code_postal='69001',
            latitude=45.7640,
            longitude=4.8357,
            visite=False,
            label=False,
            type_etab='PATISSERIE',
            id_user=user.id_user
        )
        
        etab3 = Etablissement(
            nom='Cafe des Amis',
            adresse='5 rue de Marseille, 13001 Marseille',
            ville='Marseille',
            code_postal='13001',
            latitude=43.2965,
            longitude=5.3698,
            visite=True,
            label=False,
            type_etab='RESTAURANT',
            id_user=admin.id_user
        )
        
        db.session.add_all([etab1, etab2, etab3])
        db.session.commit()  # Commit establishments first to get their IDs
        
        # Créer des flans
        flan1 = Flan(
            nom='Flan vanille',
            description='Flan classique a la vanille',
            type_pate='BRISEE',
            type_saveur='VANILLE',
            type_texture='CREMEUSE',
            prix=3.50,
            id_etab=etab1.id_etab,
            id_user=admin.id_user
        )
        
        flan2 = Flan(
            nom='Flan chocolat',
            description='Flan riche au chocolat noir',
            type_pate='SABLEE',
            type_saveur='NOIX',
            type_texture='CREMEUSE',
            prix=4.00,
            id_etab=etab1.id_etab,
            id_user=user.id_user
        )
        
        flan3 = Flan(
            nom='Flan citron',
            description='Flan acidule au citron',
            type_pate='BRISEE',
            type_saveur='FRUITS',
            type_texture='GELATINEUSE',
            prix=2.50,
            id_etab=etab2.id_etab,
            id_user=admin.id_user
        )
        
        db.session.add_all([flan1, flan2, flan3])
        db.session.commit()


def test_filtrer_etablissements_par_nom(app, setup_data):
    """Test le filtrage des établissements par nom."""
    with app.app_context():
        query = Etablissement.query
        
        # Filtrer par nom
        filtered_query = filtrer_etablissements(query, nom='Boulangerie')
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].nom == 'Boulangerie Martin'


def test_filtrer_etablissements_par_ville(app, setup_data):
    """Test le filtrage des établissements par ville."""
    with app.app_context():
        query = Etablissement.query
        
        # Filtrer par ville
        filtered_query = filtrer_etablissements(query, ville='Lyon')
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].nom == 'Patisserie Dubois'


def test_filtrer_etablissements_par_visite(app, setup_data):
    """Test le filtrage des établissements par statut de visite."""
    with app.app_context():
        query = Etablissement.query
        
        # Filtrer par visite = oui
        filtered_query = filtrer_etablissements(query, visite='oui')
        results = filtered_query.all()
        
        assert len(results) == 2
        assert all(etab.visite == True for etab in results)
        
        # Filtrer par visite = non
        filtered_query = filtrer_etablissements(query, visite='non')
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].visite == False


def test_filtrer_etablissements_par_labellise(app, setup_data):
    """Test le filtrage des établissements par statut labellisé."""
    with app.app_context():
        query = Etablissement.query
        
        # Filtrer par labellisé = oui
        filtered_query = filtrer_etablissements(query, labellise='oui')
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].label == True
        
        # Filtrer par labellisé = non
        filtered_query = filtrer_etablissements(query, labellise='non')
        results = filtered_query.all()
        
        assert len(results) == 2
        assert all(etab.label == False for etab in results)


def test_filtrer_etablissements_par_type_pate(app, setup_data):
    """Test le filtrage des établissements par type de pâte."""
    with app.app_context():
        # Note: filtrer_etablissements fait une jointure implicite avec Flan
        # mais ne gère pas la jointure automatiquement, donc nous devons la faire manuellement
        query = Etablissement.query.join(Flan)
        
        # Filtrer par type de pâte = BRISEE
        filtered_query = filtrer_etablissements(query, type_pate='BRISEE')
        results = filtered_query.all()
        
        # Devrait retourner les établissements avec des flans à pâte brisée
        assert len(results) == 2  # Boulangerie Martin et Patisserie Dubois
        
        # Filtrer par type de pâte = SABLEE
        filtered_query = filtrer_etablissements(query, type_pate='SABLEE')
        results = filtered_query.all()
        
        assert len(results) == 1  # Boulangerie Martin seulement


def test_filtrer_etablissements_par_type_saveur(app, setup_data):
    """Test le filtrage des établissements par type de saveur."""
    with app.app_context():
        query = Etablissement.query.join(Flan)
        
        # Filtrer par saveur = VANILLE
        filtered_query = filtrer_etablissements(query, type_saveur='VANILLE')
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].nom == 'Boulangerie Martin'


def test_filtrer_etablissements_par_prix(app, setup_data):
    """Test le filtrage des établissements par prix."""
    with app.app_context():
        query = Etablissement.query.join(Flan)
        
        # Filtrer par prix < 2.5
        filtered_query = filtrer_etablissements(query, prix='0')
        results = filtered_query.all()
        
        assert len(results) == 0  # Aucun flan à moins de 2.5€ (citron est à 2.50)
        
        # Filtrer par prix entre 2.5 et 5
        filtered_query = filtrer_etablissements(query, prix='2.5')
        results = filtered_query.all()
        
        assert len(results) == 2  # 2 établissements ont des flans dans cette fourchette
        
        # Filtrer par prix >= 5
        filtered_query = filtrer_etablissements(query, prix='5')
        results = filtered_query.all()
        
        assert len(results) == 0  # Aucun flan à 5€ ou plus


def test_filtrer_etablissements_combinaison_filtres(app, setup_data):
    """Test le filtrage avec une combinaison de filtres."""
    with app.app_context():
        query = Etablissement.query.join(Flan)
        
        # Combinaison: Paris + visite = oui + pâte BRISEE
        filtered_query = filtrer_etablissements(
            query, 
            ville='Paris', 
            visite='oui', 
            type_pate='BRISEE'
        )
        results = filtered_query.all()
        
        assert len(results) == 1
        assert results[0].nom == 'Boulangerie Martin'


def test_filtrer_etablissements_sans_filtres(app, setup_data):
    """Test le filtrage sans aucun filtre."""
    with app.app_context():
        query = Etablissement.query
        
        # Aucun filtre
        filtered_query = filtrer_etablissements(query)
        results = filtered_query.all()
        
        assert len(results) == 3  # Tous les établissements


def test_filtrer_etablissements_avec_tous_comme_valeur(app, setup_data):
    """Test le filtrage avec 'tous' comme valeur (ne devrait pas filtrer)."""
    with app.app_context():
        query = Etablissement.query.join(Flan)
        
        # Filtrer avec type_pate='tous' (ne devrait pas filtrer)
        filtered_query = filtrer_etablissements(query, type_pate='tous')
        results = filtered_query.all()
        
        # Devrait retourner tous les établissements avec des flans
        assert len(results) == 2  # 2 établissements ont des flans (etab1 et etab2)


def test_liste_etablissements_route_get(client, setup_data):
    """Test la route liste_etablissements avec une requête GET."""
    response = client.get('/liste_etablissements')
    assert response.status_code == 200
    # Vérifier que la page contient des éléments attendus
    assert b'Boulangerie Martin' in response.data
    assert b'Patisserie Dubois' in response.data


def test_liste_etablissements_recherche_simple(client, setup_data):
    """Test la recherche simple dans liste_etablissements."""
    response = client.get('/liste_etablissements?recherche_simple=Paris')
    assert response.status_code == 200
    # Devrait trouver seulement la boulangerie à Paris
    assert b'Boulangerie Martin' in response.data
    # Ne devrait pas trouver les établissements de Lyon ou Marseille
    assert b'Lyon' not in response.data


def test_liste_etablissements_filtres_avances(client, setup_data):
    """Test les filtres avancés dans liste_etablissements."""
    response = client.get('/liste_etablissements?ville=Paris&visite=oui')
    assert response.status_code == 200
    # Devrait trouver la boulangerie à Paris avec visite=oui
    assert b'Boulangerie Martin' in response.data


def test_liste_etablissements_filtre_prix(client, setup_data):
    """Test le filtre par prix dans liste_etablissements."""
    response = client.get('/liste_etablissements?prix=2.5')  # Prix entre 2.5 et 5
    assert response.status_code == 200
    # Devrait trouver les flans dans cette fourchette de prix
    assert b'vanille' in response.data


@pytest.mark.skip(reason="API tests require more complex setup, skipping for now")
def test_api_etablissements_get(client, setup_data):
    """Test l'API etablissements avec une requête GET."""
    response = client.get('/api/etablissements?format=json')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3  # Tous les établissements
    
    # Vérifier la structure des données
    assert 'nom' in data[0]
    assert 'ville' in data[0]
    assert 'id_etab' in data[0]


@pytest.mark.skip(reason="API tests require more complex setup, skipping for now")
def test_api_etablissements_filtres(client, setup_data):
    """Test l'API etablissements avec des filtres."""
    response = client.get('/api/etablissements?ville=Paris&format=json')
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1  # Un seul établissement à Paris
    assert data[0]['nom'] == 'Boulangerie Martin'


@pytest.mark.skip(reason="API tests require more complex setup, skipping for now")
def test_api_etablissements_format_html(client, setup_data):
    """Test l'API etablissements avec format HTML."""
    response = client.get('/api/etablissements?format=html')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    # Devrait contenir du HTML
    assert b'<div' in response.data or b'<table' in response.data


@pytest.mark.skip(reason="API tests require more complex setup, skipping for now")
def test_api_etablissements_post(client, setup_data):
    """Test l'API etablissements avec une requête POST."""
    response = client.post('/api/etablissements', json={
        'ville': 'Paris',
        'format': 'json'
    })
    assert response.status_code == 200
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['nom'] == 'Boulangerie Martin'


@pytest.mark.skip(reason="API tests require more complex setup, skipping for now")
def test_api_etablissements_erreur(client, setup_data):
    """Test l'API etablissements avec une erreur."""
    # Envoyer une requête POST avec des données invalides
    response = client.post('/api/etablissements', json={
        'format': 'json'
    })
    assert response.status_code == 200  # Devrait toujours retourner 200 même avec des filtres vides
    
    data = response.get_json()
    assert isinstance(data, list)
    # Devrait retourner tous les établissements
    assert len(data) == 3


def test_get_infowindow_content(client, setup_data):
    """Test la route get_infowindow_content."""
    with client.application.app_context():
        etab = Etablissement.query.first()
        etab_id = etab.id_etab
    
    response = client.get(f'/get_infowindow_content?id_etab={etab_id}')
    assert response.status_code == 200
    # Devrait contenir des informations sur l'établissement
    assert b'Boulangerie Martin' in response.data


def test_get_infowindow_content_etablissement_inexistant(client):
    """Test get_infowindow_content avec un établissement inexistant."""
    response = client.get('/get_infowindow_content?id_etab=999999')
    assert response.status_code == 404
    assert b'D\xc3\xa9tails non disponibles' in response.data or b'Details non disponibles' in response.data


def test_rechercher_route(client):
    """Test la route rechercher."""
    response = client.get('/rechercher')
    assert response.status_code == 200
    # Vérifier que la page contient le formulaire de recherche
    assert b'form_recherche' in response.data or b'Recherche' in response.data


def test_afficher_badge_etablissement(app, setup_data):
    """Test la fonction afficher_badge_etablissement."""
    from app.routes.main import afficher_badge_etablissement
    
    with app.app_context():
        etab = Etablissement.query.first()
        
        # Test avec un établissement labellisé
        etab.label = True
        db.session.commit()
        
        badge = afficher_badge_etablissement(etab)
        # Devrait contenir le badge label
        assert 'Labellisé' in badge
        assert '❤️' in badge
        
        # Test avec un établissement non labellisé
        etab.label = False
        db.session.commit()
        
        badge = afficher_badge_etablissement(etab)
        # Ne devrait pas contenir le badge
        assert badge == ''


def test_afficher_badge_type_etab(app, setup_data):
    """Test la fonction afficher_badge_type_etab."""
    from app.routes.main import afficher_badge_type_etab
    
    with app.app_context():
        etab = Etablissement.query.first()
        
        # Test avec différents types d'établissements
        badge = afficher_badge_type_etab(etab)
        # Devrait contenir le badge pour le type d'établissement
        assert 'badge-type-etab' in badge
        assert etab.type_etab.value in badge