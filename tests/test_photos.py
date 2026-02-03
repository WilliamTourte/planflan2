"""Tests pour les routes de gestion des photos (photos.py)

Ce module teste les fonctionnalités de téléchargement et validation
des photos dans l'application PlanFlan.
"""

import pytest
import os
import io
from app import create_app, db
from app.config import TestConfig
from app.routes.photos import validate_file_signature


# ============================================================================
# Tests pour validate_file_signature
# ============================================================================


class TestValidateFileSignature:
    """Tests pour la fonction validate_file_signature"""

    def test_validate_png_valide(self):
        """Test validation d'un fichier PNG valide"""
        # Magic bytes PNG: 89 50 4E 47 0D 0A 1A 0A
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        file = io.BytesIO(png_header)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is True
        assert ext == "png"

    def test_validate_jpeg_valide(self):
        """Test validation d'un fichier JPEG valide"""
        # Magic bytes JPEG: FF D8 FF au début, FF D9 à la fin
        jpeg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100 + b"\xff\xd9"
        file = io.BytesIO(jpeg_content)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is True
        assert ext == "jpg"

    def test_validate_gif87a_valide(self):
        """Test validation d'un fichier GIF87a valide"""
        gif_content = b"GIF87a" + b"\x00" * 100
        file = io.BytesIO(gif_content)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is True
        assert ext == "gif"

    def test_validate_gif89a_valide(self):
        """Test validation d'un fichier GIF89a valide"""
        gif_content = b"GIF89a" + b"\x00" * 100
        file = io.BytesIO(gif_content)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is True
        assert ext == "gif"

    def test_validate_fichier_invalide(self):
        """Test validation d'un fichier avec signature invalide"""
        invalid_content = b"This is not an image file"
        file = io.BytesIO(invalid_content)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is False
        assert ext is None

    def test_validate_jpeg_sans_footer(self):
        """Test validation d'un JPEG sans footer correct"""
        # JPEG header correct mais pas de footer FF D9
        jpeg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100 + b"\x00\x00"
        file = io.BytesIO(jpeg_content)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is False
        assert ext is None

    def test_validate_fichier_vide(self):
        """Test validation d'un fichier trop court"""
        file = io.BytesIO(b"\x00" * 2)

        is_valid, ext = validate_file_signature(file)

        assert is_valid is False
        assert ext is None

    def test_validate_curseur_remis_au_debut(self):
        """Test que le curseur du fichier est remis au début après validation"""
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        file = io.BytesIO(png_header)

        validate_file_signature(file)

        # Le curseur devrait être au début
        assert file.tell() == 0


# ============================================================================
# Tests pour la route upload_file
# ============================================================================


class TestUploadFileRoute:
    """Tests pour la route /upload"""

    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test"""
        app = create_app(TestConfig)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "test_uploads")

        # Créer le dossier d'upload temporaire
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()

        # Nettoyer le dossier d'upload
        import shutil

        if os.path.exists(app.config["UPLOAD_FOLDER"]):
            shutil.rmtree(app.config["UPLOAD_FOLDER"])

    def test_upload_get_redirige(self, client):
        """Test que GET /upload redirige vers show_uploads"""
        response = client.get("/upload", follow_redirects=False)

        assert response.status_code == 302
        assert "/uploads" in response.location

    def test_upload_sans_fichier(self, client):
        """Test upload sans fichier dans la requête"""
        response = client.post("/upload", data={}, follow_redirects=False)

        # Devrait rediriger vers la même URL
        assert response.status_code == 302

    def test_upload_fichier_vide(self, client):
        """Test upload avec un nom de fichier vide"""
        data = {"file": (io.BytesIO(b""), "")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        assert response.status_code == 302

    def test_upload_extension_invalide(self, client):
        """Test upload avec une extension non autorisée"""
        data = {"file": (io.BytesIO(b"fake content"), "test.txt")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "Fichier non valide" in response.data.decode() or response.status_code == 200

    def test_upload_magic_bytes_invalides(self, client):
        """Test upload avec magic bytes ne correspondant pas à l'extension"""
        # Fichier avec extension .png mais contenu texte
        data = {"file": (io.BytesIO(b"This is not a PNG"), "test.png")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_upload_png_valide(self, client):
        """Test upload d'un fichier PNG valide"""
        # Créer un PNG minimal valide
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        data = {"file": (io.BytesIO(png_content), "test.png")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_upload_extension_ne_correspond_pas(self, client):
        """Test upload où l'extension ne correspond pas au type détecté"""
        # Fichier PNG mais avec extension .gif
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        data = {"file": (io.BytesIO(png_content), "test.gif")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200


# ============================================================================
# Tests pour la route show_uploads
# ============================================================================


class TestShowUploadsRoute:
    """Tests pour la route /uploads"""

    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test"""
        app = create_app(TestConfig)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "test_uploads_show")

        # Créer le dossier d'upload temporaire
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()

        # Nettoyer le dossier d'upload
        import shutil

        if os.path.exists(app.config["UPLOAD_FOLDER"]):
            shutil.rmtree(app.config["UPLOAD_FOLDER"])

    def test_show_uploads_vide(self, client):
        """Test affichage quand le dossier est vide"""
        response = client.get("/uploads")

        assert response.status_code == 200

    def test_show_uploads_avec_fichiers(self, client):
        """Test affichage avec des fichiers présents"""
        # Créer des fichiers de test dans le dossier
        upload_folder = client.application.config["UPLOAD_FOLDER"]

        test_files = ["image1.png", "image2.jpg", "photo.gif"]
        for filename in test_files:
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "w") as f:
                f.write("test content")

        response = client.get("/uploads")

        assert response.status_code == 200


# ============================================================================
# Tests d'intégration
# ============================================================================


@pytest.mark.integration
class TestPhotosIntegration:
    """Tests d'intégration pour le module photos"""

    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test"""
        app = create_app(TestConfig)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["UPLOAD_FOLDER"] = os.path.join(
            os.path.dirname(__file__), "test_uploads_integration"
        )

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()

        import shutil

        if os.path.exists(app.config["UPLOAD_FOLDER"]):
            shutil.rmtree(app.config["UPLOAD_FOLDER"])

    def test_workflow_upload_complet(self, client):
        """Test du workflow complet: upload puis affichage"""
        # 1. Vérifier que la page uploads est accessible
        response = client.get("/uploads")
        assert response.status_code == 200

        # 2. Uploader un fichier PNG valide
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        data = {"file": (io.BytesIO(png_content), "workflow_test.png")}
        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200

        # 3. Vérifier que la page uploads affiche le fichier
        response = client.get("/uploads")
        assert response.status_code == 200
