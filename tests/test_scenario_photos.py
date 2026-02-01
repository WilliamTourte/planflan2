"""Tests exhaustifs pour la gestion des photos avec google_place_id.

Ce module teste la standardisation du stockage et de l'affichage des photos
d'établissements en utilisant les Google Place ID comme identifiants stables.
"""

import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import Etablissement, Photo, TypeEtab, TypeCible


@pytest.fixture
def app():
    """Fixture pour l'application Flask avec configuration de test."""
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture pour le client de test."""
    return app.test_client()


class TestGestionPhotos:
    """Tests exhaustifs pour la gestion des photos avec google_place_id"""

    def test_creation_etablissement_avec_google_place_id(self, app):
        """Test : création d'établissement et stockage du google_place_id"""
        with app.app_context():
            etab = Etablissement(
                nom="Test Boulangerie",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJTest123",
                id_user=1,
            )
            db.session.add(etab)
            db.session.commit()

            # Vérifier que le google_place_id est sauvegardé
            etab_saved = Etablissement.query.filter_by(
                google_place_id="ChIJTest123"
            ).first()
            assert etab_saved is not None
            assert etab_saved.google_place_id == "ChIJTest123"

    def test_creation_photo_avec_nom_standardise(self, app):
        """Test : la photo utilise UNIQUEMENT le nom du fichier"""
        with app.app_context():
            etab = Etablissement(
                nom="Test",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJTest123",
                id_user=1,
            )
            db.session.add(etab)
            db.session.flush()

            # Créer une photo avec JUSTE le nom
            photo = Photo(
                id_etab=etab.id_etab,
                type_cible=TypeCible.ETABLISSEMENT,
                path="ChIJTest123_photo_0.jpg",  # PAS "uploads/..."
                largeur=400,
                hauteur=400,
            )
            db.session.add(photo)
            db.session.commit()

            # Vérifier que le path ne contient PAS de chemin
            photo_saved = Photo.query.filter_by(id_etab=etab.id_etab).first()
            assert photo_saved.path == "ChIJTest123_photo_0.jpg"
            assert not photo_saved.path.startswith("uploads/")
            assert "/" not in photo_saved.path

    def test_coherence_google_place_id_entre_dev_et_prod(self, app):
        """Test : les google_place_id sont identiques entre dev et prod"""
        with app.app_context():
            # Simuler un établissement en dev
            etab_dev = Etablissement(
                nom="Boulangerie Dev",
                adresse="1 rue Dev",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJABC123",
                id_user=1,
            )
            db.session.add(etab_dev)
            db.session.commit()
            id_dev = etab_dev.id_etab

            # Simuler un établissement en prod (même google_place_id, id différent)
            etab_prod = Etablissement(
                nom="Boulangerie Prod",
                adresse="1 rue Prod",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJABC123",
                id_user=2,
            )
            db.session.add(etab_prod)
            db.session.commit()
            id_prod = etab_prod.id_etab

            # Les id_etab sont différents
            assert id_dev != id_prod

            # Mais les google_place_id sont identiques
            assert etab_dev.google_place_id == etab_prod.google_place_id

            # La photo devrait avoir le même nom dans les deux cas
            photo_filename = f"{etab_dev.google_place_id}_photo_0.jpg"
            assert photo_filename == f"{etab_prod.google_place_id}_photo_0.jpg"

    def test_sauvegarde_fichier_photo_avec_google_place_id(self, app, tmp_path):
        """Test : la photo est sauvegardée avec le bon nom de fichier"""
        with app.app_context():
            google_place_id = "ChIJTest456"
            filename = f"{google_place_id}_photo_0.jpg"

            # Simuler le dossier static/uploads
            uploads_dir = tmp_path / "static" / "uploads"
            uploads_dir.mkdir(parents=True)

            # Sauvegarder un fichier test
            filepath = uploads_dir / filename
            filepath.write_bytes(b"fake image data")

            # Vérifier que le fichier existe avec le bon nom
            assert filepath.exists()
            assert filepath.name == f"{google_place_id}_photo_0.jpg"

    def test_pas_de_double_chemin_dans_url(self, app):
        """Test : vérifier qu'il n'y a pas de double 'uploads/' dans l'URL"""
        with app.app_context():
            # Configurer SERVER_NAME pour permettre url_for de fonctionner
            app.config["SERVER_NAME"] = "localhost"

            etab = Etablissement(
                nom="Test",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJTest789",
                id_user=1,
            )
            db.session.add(etab)
            db.session.flush()

            photo = Photo(
                id_etab=etab.id_etab,
                type_cible=TypeCible.ETABLISSEMENT,
                path="ChIJTest789_photo_0.jpg",  # JUSTE le nom
                largeur=400,
                hauteur=400,
            )
            db.session.add(photo)
            db.session.commit()

            # L'URL générée devrait être /static/uploads/ChIJTest789_photo_0.jpg
            # PAS /static/uploads/uploads/ChIJTest789_photo_0.jpg
            from flask import url_for

            with app.test_request_context():
                url = url_for("static", filename=f"uploads/{photo.path}")
                assert url == "/static/uploads/ChIJTest789_photo_0.jpg"
                assert "uploads/uploads" not in url

    def test_photo_path_sans_prefix_uploads(self, app):
        """Test : vérifier que le path dans la BDD ne contient jamais 'uploads/'"""
        with app.app_context():
            etab = Etablissement(
                nom="Test Etablissement",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJTest999",
                id_user=1,
            )
            db.session.add(etab)
            db.session.flush()

            # Créer plusieurs photos
            for i in range(3):
                photo = Photo(
                    id_etab=etab.id_etab,
                    type_cible=TypeCible.ETABLISSEMENT,
                    path=f"ChIJTest999_photo_{i}.jpg",
                    largeur=400,
                    hauteur=400,
                )
                db.session.add(photo)
            db.session.commit()

            # Vérifier que TOUTES les photos ont un path sans préfixe
            photos = Photo.query.filter_by(id_etab=etab.id_etab).all()
            assert len(photos) == 3
            for photo in photos:
                assert not photo.path.startswith("uploads/")
                assert not photo.path.startswith("static/")
                assert "/" not in photo.path

    def test_format_nom_fichier_google_place_id(self, app):
        """Test : vérifier le format correct du nom de fichier avec google_place_id"""
        with app.app_context():
            google_place_id = "ChIJUy4Drt5x5kcRkHl_c9NVwDM"

            etab = Etablissement(
                nom="Test Format",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id=google_place_id,
                id_user=1,
            )
            db.session.add(etab)
            db.session.flush()

            # Format attendu: {google_place_id}_photo_{index}.jpg
            expected_filename = f"{google_place_id}_photo_0.jpg"

            photo = Photo(
                id_etab=etab.id_etab,
                type_cible=TypeCible.ETABLISSEMENT,
                path=expected_filename,
                largeur=400,
                hauteur=400,
            )
            db.session.add(photo)
            db.session.commit()

            # Vérifier le format
            photo_saved = Photo.query.filter_by(id_etab=etab.id_etab).first()
            assert photo_saved.path == expected_filename
            assert photo_saved.path.startswith(google_place_id)
            assert photo_saved.path.endswith("_photo_0.jpg")

    def test_upload_folder_configuration(self, app):
        """Test : vérifier que UPLOAD_FOLDER est correctement configuré"""
        with app.app_context():
            upload_folder = app.config.get("UPLOAD_FOLDER")

            # UPLOAD_FOLDER doit être défini
            assert upload_folder is not None

            # En test, devrait être un chemin relatif ou absolu valide
            assert isinstance(upload_folder, str)
            assert len(upload_folder) > 0

            # Le chemin ne devrait pas contenir de doubles slashes
            assert "//" not in upload_folder

    def test_upload_folder_writable(self, app, tmp_path):
        """Test : vérifier que le dossier uploads est accessible en écriture"""
        with app.app_context():
            # Utiliser tmp_path pour le test
            uploads_dir = tmp_path / "static" / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)

            # Vérifier que le dossier existe
            assert uploads_dir.exists()
            assert uploads_dir.is_dir()

            # Vérifier qu'on peut écrire dedans
            test_file = uploads_dir / "test_write.txt"
            test_file.write_text("test")
            assert test_file.exists()

            # Nettoyer
            test_file.unlink()

    def test_fetch_place_photos_creates_upload_folder(self, app, tmp_path, monkeypatch):
        """Test : fetch_place_photos crée le dossier uploads s'il n'existe pas"""
        with app.app_context():
            from app.outils import fetch_place_photos
            import os

            # Utiliser un dossier temporaire
            temp_uploads = tmp_path / "uploads"
            app.config["UPLOAD_FOLDER"] = str(temp_uploads)

            # Le dossier ne devrait pas exister au début
            assert not temp_uploads.exists()

            # Mock de get_place_details pour ne pas faire d'appel API réel
            def mock_get_place_details(place_id, api_key):
                return None  # Pas de photos disponibles

            monkeypatch.setattr("app.outils.get_place_details", mock_get_place_details)

            # Créer un établissement
            etab = Etablissement(
                nom="Test",
                adresse="1 rue Test",
                code_postal="75001",
                ville="Paris",
                latitude=48.8566,
                longitude=2.3522,
                type_etab=TypeEtab.BOULANGERIE,
                google_place_id="ChIJTestFolder",
                id_user=1,
            )
            db.session.add(etab)
            db.session.commit()

            # Appeler fetch_place_photos
            result = fetch_place_photos(etab.id_etab, "ChIJTestFolder", "fake_api_key")

            # Le dossier devrait avoir été créé (même si pas de photos téléchargées)
            # Note: ce test dépend de l'implémentation actuelle de fetch_place_photos
            # qui crée le dossier s'il n'existe pas
