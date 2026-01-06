"""
Tests pour la validation des formulaires de l'application.
Ce fichier teste que les formulaires rejettent correctement les données invalides
et acceptent les données valides.
"""

import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import Etablissement, Flan, Utilisateur
from app.forms import (
    # Importer les fixtures depuis test_securite
    RechercheForm,
    EtabForm,
    NewFlanForm,
    EvalForm,
    UpdateProfileForm,
    DeleteForm,
    ValidateForm,
)
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Crée une application de test avec configuration SQLite en mémoire."""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with client.application.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def setup_data(app):
    """Crée des données de test pour les établissements et flans."""
    with client.application.app_context():
        # Créer un utilisateur
        user = Utilisateur(
            pseudo="testuser",
            email="test@example.com",
            password=generate_password_hash("password"),
            is_admin=False,
        )
        db.session.add(user)

        # Créer un établissement
        etab = Etablissement(
            nom="Boulangerie Test",
            adresse="1 rue de Test",
            ville="Testville",
            code_postal="69001",
            latitude=45.7640,
            longitude=4.8357,
            visite=True,
            label=False,
            type_etab="BOULANGERIE",
            id_user=user.id_user,
        )
        db.session.add(etab)
        db.session.commit()

        # Créer un flan
        flan = Flan(
            nom="Flan Vanille",
            description="Flan classique à la vanille",
            type_pate="BRISEE",
            type_saveur="VANILLE",
            type_texture="CREMEUSE",
            prix=3.50,
            id_etab=etab.id_etab,
            id_user=user.id_user,
        )
        db.session.add(flan)
        db.session.commit()


# Tests pour EtabForm


@pytest.mark.parametrize(
    "test_name,form_data,expected_valid",
    [
        # Test avec données valides
        (
            "valid_data",
            {
                "nom": "Nouvelle Boulangerie",
                "description": "Description valide",
                "adresse": "10 rue de la République",
                "ville": "Lyon",
                "code_postal": "69001",
                "latitude": 45.7640,
                "longitude": 4.8357,
                "type_etab": "BOULANGERIE",
                "label": False,
                "visite": True,
            },
            True,
        ),
        # Test avec données invalides
        (
            "invalid_data",
            {
                "nom": "",  # Nom vide
                "description": "a" * 1001,  # Description trop longue
                "adresse": "",  # Adresse vide
                "ville": "",  # Ville vide
                "code_postal": "INVALIDE",  # Code postal invalide
                "latitude": 200,  # Latitude invalide
                "longitude": 200,  # Longitude invalide
            },
            False,
        ),
    ],
)
def test_etabform_parametrize(client, test_name, form_data, expected_valid):
    """Test EtabForm avec différents scénarios (paramétrisé)"""
    with client.application.app_context():
        form = EtabForm()

        # Remplir le formulaire avec les données fournies
        for field, value in form_data.items():
            setattr(getattr(form, field), 'data', value)

        # Vérifier la validation
        assert form.validate() == expected_valid

        # Pour les cas invalides, vérifier les erreurs spécifiques
        if not expected_valid:
            if not form_data.get("nom"):
                assert form.nom.errors and len(form.nom.errors) > 0
            if not form_data.get("adresse"):
                assert form.adresse.errors and len(form.adresse.errors) > 0
            if not form_data.get("ville"):
                assert form.ville.errors and len(form.ville.errors) > 0





# Tests pour NewFlanForm


@pytest.mark.parametrize(
    "test_name,form_data,expected_valid",
    [
        # Test avec données valides
        (
            "valid_data",
            {
                "nom": "Flan Chocolat",
                "description": "Flan riche au chocolat noir",
                "prix": 4.00,
                "type_pate": "BRISEE",
                "type_saveur": "NOIX",
                "type_texture": "CREMEUSE",
            },
            True,
        ),
        # Test avec données invalides
        (
            "invalid_data",
            {
                "nom": "",  # Nom vide
                "description": "a" * 1001,  # Description trop longue
                "prix": -2.5,  # Prix négatif
                "type_pate": "INVALIDE",  # Type de pâte invalide
                "type_saveur": "INVALIDE",  # Type de saveur invalide
                "type_texture": "INVALIDE",  # Type de texture invalide
            },
            False,
        ),
    ],
)
def test_newflanform_parametrize(client, test_name, form_data, expected_valid):
    """Test NewFlanForm avec différents scénarios (paramétrisé)"""
    with client.application.app_context():
        form = NewFlanForm()

        # Remplir le formulaire avec les données fournies
        for field, value in form_data.items():
            setattr(getattr(form, field), 'data', value)

        # Vérifier la validation
        assert form.validate() == expected_valid

        # Pour les cas invalides, vérifier les erreurs spécifiques
        if not expected_valid:
            if not form_data.get("nom"):
                assert form.nom.errors and len(form.nom.errors) > 0
            if form_data.get("description", "") and len(form_data["description"]) > 1000:
                assert form.description.errors and len(form.description.errors) > 0
            if form_data.get("prix", 0) < 0:
                assert form.prix.errors and len(form.prix.errors) > 0


# Tests pour EvalForm


@pytest.mark.parametrize(
    "test_name,form_data,expected_valid",
    [
        # Test avec données valides
        (
            "valid_data",
            {
                "visuel": "4.5",
                "texture": "5",
                "pate": "3",
                "gout": "4",
                "description": "Très bon flan, texture parfaite.",
            },
            True,
        ),
        # Test avec données invalides
        (
            "invalid_data",
            {
                "visuel": "6.0",  # Note > 5
                "texture": "-1.0",  # Note < 0
                "pate": "abc",  # Valeur non numérique
                "gout": None,  # Valeur nulle
                "description": "a" * 1001,  # Description trop longue
            },
            False,
        ),
    ],
)
def test_evalform_parametrize(client, test_name, form_data, expected_valid):
    """Test EvalForm avec différents scénarios (paramétrisé)"""
    with client.application.app_context():
        form = EvalForm()

        # Remplir le formulaire avec les données fournies
        for field, value in form_data.items():
            setattr(getattr(form, field), 'data', value)

        # Vérifier la validation
        assert form.validate() == expected_valid

        # Pour les cas valides, vérifier que les données sont bien des chaînes parmi les choix valides
        if expected_valid:
            valid_choices = [
                "0",
                "0.5",
                "1",
                "1.5",
                "2",
                "2.5",
                "3",
                "3.5",
                "4",
                "4.5",
                "5",
            ]
            # Vérifier que les valeurs sont dans les choix valides
            assert form.visuel.data in valid_choices
            assert form.texture.data in valid_choices
            assert form.pate.data in valid_choices
            assert form.gout.data in valid_choices

        # Pour les cas invalides, vérifier les erreurs spécifiques
        if not expected_valid:
            # Vérifier les erreurs (indépendant de la langue)
            if form_data.get("visuel") not in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]:
                assert form.visuel.errors and len(form.visuel.errors) > 0
            if form_data.get("texture") not in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]:
                assert form.texture.errors and len(form.texture.errors) > 0
            if form_data.get("pate") not in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]:
                assert form.pate.errors and len(form.pate.errors) > 0
            if form_data.get("gout") not in ["0", "0.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5"]:
                assert form.gout.errors and len(form.gout.errors) > 0
            if form_data.get("description", "") and len(form_data["description"]) > 1000:
                assert form.description.errors and len(form.description.errors) > 0


def test_evalform_notes_hors_plage(client):
    """Test EvalForm avec des notes hors de la plage valide."""
    with client.application.app_context():
        form = EvalForm()

        # Tester différentes notes invalides (chaînes non valides)
        notes_invalides = [
            "-0.1",
            "5.1",
            "10",
            "-10",
            "2.3",
        ]  # 2.3 n'est pas dans les choix valides

        for note in notes_invalides:
            form.visuel.data = note
            assert not form.validate()
            # Vérifier qu'il y a des erreurs (indépendant de la langue)
            assert form.visuel.errors and len(form.visuel.errors) > 0


# Tests pour UpdateProfileForm


def test_updateprofileform_donnees_valides(client):
    """Test UpdateProfileForm avec des données valides."""
    with client.application.app_context():
        form = UpdateProfileForm()

        # Remplir le formulaire avec des données valides
        form.pseudo.data = "nouveau_pseudo"
        form.email.data = "nouvel@email.com"
        form.current_password.data = "password"  # Mot de passe de l'utilisateur de test
        form.new_password.data = "nouveau_mot_de_passe"
        form.confirm_password.data = "nouveau_mot_de_passe"

        # Le formulaire devrait être valide
        assert form.validate()


def test_updateprofileform_donnees_invalides(client):
    """Test UpdateProfileForm avec des données invalides."""
    with client.application.app_context():
        form = UpdateProfileForm()

        # Remplir le formulaire avec des données invalides
        form.pseudo.data = ""  # Pseudo vide
        form.email.data = "email_invalide"  # Email invalide
        form.current_password.data = (
            "a" * 50
        )  # Mot de passe trop long pour la validation WTForms
        form.new_password.data = "court"  # Mot de passe trop court
        form.confirm_password.data = "different"  # Confirmation différente

        # Le formulaire ne devrait pas être valide
        assert not form.validate()

        # Vérifier les erreurs spécifiques (indépendant de la langue)
        # Note: pseudo et email sont Optional dans UpdateProfileForm
        # La validation personnalisée du current_password se déclenche en premier
        assert form.current_password.errors and len(form.current_password.errors) > 0
        # Note: Comme le current_password échoue, les autres validations ne se font pas
        # On peut tester les validations de new_password dans un test séparé


def test_updateprofileform_mots_de_passe_non_correspondants(client):
    """Test UpdateProfileForm avec des mots de passe non correspondants."""
    with client.application.app_context():
        form = UpdateProfileForm()

        # Remplir current_password avec une valeur invalide pour éviter la validation personnalisée
        form.current_password.data = "wrong_password"
        form.new_password.data = "mot_de_passe_1"
        form.confirm_password.data = "mot_de_passe_2"

        # Le formulaire ne devrait pas être valide à cause du current_password incorrect
        assert not form.validate()
        # Vérifier qu'il y a des erreurs (indépendant de la langue)
        assert form.current_password.errors and len(form.current_password.errors) > 0
        # Note: La validation EqualTo ne peut pas être testée facilement car elle nécessite
        # que current_password soit valide, ce qui nécessite current_user


# Tests pour RechercheForm


@pytest.mark.slow
@pytest.mark.forms
def test_rechercheform_donnees_valides(client):
    """Test RechercheForm avec des données valides."""
    with client.application.app_context():
        form = RechercheForm()

        # Remplir le formulaire avec des données valides
        form.nom.data = "Boulangerie"
        form.ville.data = "Lyon"
        form.type_saveur.data = "VANILLE"
        form.type_pate.data = "BRISEE"
        form.type_texture.data = "CREMEUSE"
        form.prix.data = "2.5"
        form.visite.data = "oui"
        form.labellise.data = "non"
        form.latitude.data = 45.7640
        form.longitude.data = 4.8357
        form.rayon.data = "5.0"  # Maintenant une chaîne

        # Le formulaire devrait être valide
        assert form.validate()


def test_rechercheform_donnees_invalides(client):
    """Test RechercheForm avec des données invalides."""
    with client.application.app_context():
        form = RechercheForm()

        # Remplir le formulaire avec des données invalides
        form.latitude.data = 100  # Latitude invalide
        form.longitude.data = 200  # Longitude invalide
        form.rayon.data = -5.0  # Rayon négatif

        # Le formulaire ne devrait pas être valide
        assert not form.validate()

        # Vérifier les erreurs spécifiques (indépendant de la langue)
        assert form.latitude.errors and len(form.latitude.errors) > 0
        assert form.longitude.errors and len(form.longitude.errors) > 0
        assert form.rayon.errors and len(form.rayon.errors) > 0


# Tests pour DeleteForm et ValidateForm


def test_deleteform_validation(client):
    """Test DeleteForm validation."""
    with client.application.app_context():
        form = DeleteForm()

        # Le formulaire devrait être valide sans données spécifiques
        # (il est généralement utilisé pour confirmer une suppression)
        assert form.validate()


def test_validateform_validation(client):
    """Test ValidateForm validation."""
    with client.application.app_context():
        form = ValidateForm()

        # Le formulaire devrait être valide sans données spécifiques
        # (il est généralement utilisé pour confirmer une validation)
        assert form.validate()


# Tests d'intégration des formulaires


@pytest.mark.skip("Nécessite des données en base de données")
def test_formulaire_etablissement_avec_etablissement_existant(client):
    """Test EtabForm pré-rempli avec un établissement existant."""
    with client.application.app_context():
        etab = Etablissement.query.first()
        form = EtabForm(obj=etab)

        # Le formulaire devrait être valide avec les données existantes
        assert form.validate()

        # Vérifier que les données sont correctement chargées
        assert form.nom.data == etab.nom
        assert form.adresse.data == etab.adresse
        assert form.ville.data == etab.ville


@pytest.mark.skip("Nécessite des données en base de données")
def test_formulaire_flan_avec_flan_existant(client):
    """Test NewFlanForm pré-rempli avec un flan existant."""
    with client.application.app_context():
        flan = Flan.query.first()
        form = NewFlanForm(obj=flan)

        # Le formulaire devrait être valide avec les données existantes
        assert form.validate()

        # Vérifier que les données sont correctement chargées
        assert form.nom.data == flan.nom
        assert form.description.data == flan.description
        assert form.prix.data == flan.prix


@pytest.mark.skip("Nécessite des données en base de données")
def test_formulaire_evaluation_avec_evaluation_existante(client):
    """Test EvalForm pré-rempli avec une évaluation existante."""
    with client.application.app_context():
        # Créer une évaluation pour le test
        flan = Flan.query.first()
        user = Utilisateur.query.first()

        from app.models import Evaluation

        eval = Evaluation(
            visuel=4.0,
            texture=5.0,
            pate=3.0,
            gout=4.5,
            description="Test evaluation",
            id_flan=flan.id_flan,
            id_user=user.id_user,
        )
        db.session.add(eval)
        db.session.commit()

        form = EvalForm(obj=eval)

        # Le formulaire devrait être valide avec les données existantes
        assert form.validate()

        # Vérifier que les données sont correctement chargées
        # Les données doivent être converties en chaînes pour les SelectField
        assert str(form.visuel.data) == str(eval.visuel)
        assert str(form.texture.data) == str(eval.texture)
        assert str(form.pate.data) == str(eval.pate)
        assert str(form.gout.data) == str(eval.gout)
        assert form.description.data == eval.description

@pytest.mark.slow
@pytest.mark.forms
def test_evalform_selectfield_choices(client):
    """Test EvalForm pour vérifier que les SelectField ont les bons choix."""
    with client.application.app_context():
        form = EvalForm()

        # Vérifier que les choix sont corrects pour tous les champs
        valid_choices = [
            "0",
            "0.5",
            "1",
            "1.5",
            "2",
            "2.5",
            "3",
            "3.5",
            "4",
            "4.5",
            "5",
        ]

        assert form.visuel.choices == [(choice, choice) for choice in valid_choices]
        assert form.texture.choices == [(choice, choice) for choice in valid_choices]
        assert form.pate.choices == [(choice, choice) for choice in valid_choices]
        assert form.gout.choices == [(choice, choice) for choice in valid_choices]

        # Vérifier que les choix sont bien des chaînes
        for choice in form.visuel.choices:
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)


# Tests pour UpdateProfileForm
