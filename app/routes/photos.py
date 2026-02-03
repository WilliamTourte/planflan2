"""Module des routes de gestion des photos de l'application PlanFlan.

Ce module gère le téléchargement et la gestion des photos,
otamment pour les établissements et les flans.
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    current_app,
    flash,
)
import os
from werkzeug.utils import secure_filename
from app.outils import verifier_csrf_token

photos_bp = Blueprint("photos", __name__)


def validate_file_signature(file):
    """Valide le type de fichier en vérifiant les magic bytes (signature du fichier).

    Args:
        file: L'objet fichier uploadé (Werkzeug FileStorage)

    Returns:
        tuple: (bool, str) - (True, extension) si valide, (False, None) sinon
    """
    # Lire les premiers bytes du fichier
    file.seek(0)
    header = file.read(8)
    file.seek(0)  # Remettre le curseur au début

    # Signatures magic bytes pour les formats supportés
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True, "png"

    # JPEG: FF D8 FF (suivi de E0, E1, E2, etc.)
    if header[:3] == b"\xff\xd8\xff":
        # Vérifier aussi la fin du fichier pour JPEG (FF D9)
        file.seek(-2, 2)  # Aller à 2 bytes de la fin
        footer = file.read(2)
        file.seek(0)  # Remettre le curseur au début
        if footer == b"\xff\xd9":
            return True, "jpg"

    # GIF: GIF87a ou GIF89a
    if header[:6] in (b"GIF87a", b"GIF89a"):
        return True, "gif"

    return False, None


@photos_bp.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Gère le téléchargement de fichiers image.

    Cette route permet aux utilisateurs de télécharger des images
    pour les établissements ou les flans. Elle valide le token CSRF,
    vérifie le type de fichier et enregistre l'image dans le dossier approprié.

    Returns:
        Response: Redirection vers la page d'upload avec confirmation ou erreur
    """
    # Pour les requêtes GET, rediriger vers la page d'upload
    if request.method == "GET":
        return redirect(url_for("photos.show_uploads"))

    # Vérifier le token CSRF pour les requêtes POST
    csrf_valide, message = verifier_csrf_token()
    if not csrf_valide:
        flash(message or "Token CSRF invalide. Veuillez réessayer.", "danger")
        return redirect(url_for("photos.show_uploads"))

    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)
    if file:
        # Valider l'extension du fichier
        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            flash("Fichier non valide. Veuillez téléverser une image.", "danger")
            return redirect(url_for("photos.show_uploads"))

        # Valider le contenu du fichier par magic bytes
        is_valid, detected_ext = validate_file_signature(file)
        if not is_valid:
            flash(
                "Le fichier n'est pas une image valide. Le type de fichier ne correspond pas à l'extension.",
                "danger",
            )
            return redirect(url_for("photos.show_uploads"))

        # Vérifier que l'extension correspond au type détecté
        filename_lower = file.filename.lower()
        extension_map = {"png": (".png",), "jpg": (".jpg", ".jpeg"), "gif": (".gif",)}
        if detected_ext and not filename_lower.endswith(extension_map.get(detected_ext, ())):
            flash(
                "L'extension du fichier ne correspond pas au type de fichier détecté.",
                "danger",
            )
            return redirect(url_for("photos.show_uploads"))

        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        flash("Fichier téléversé avec succès!", "success")
        return redirect(url_for("photos.show_uploads"))


@photos_bp.route("/uploads")
def show_uploads():
    """Display list of all uploaded files in the uploads folder.

    Retrieves the list of files stored in the configured UPLOAD_FOLDER
    and renders them in the upload template for viewing and management.

    Returns:
        Response: Rendered HTML template with list of uploaded files
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    if os.path.exists(upload_folder):
        uploads = os.listdir(upload_folder)
    else:
        uploads = []
    return render_template("upload.html", uploads=uploads)
