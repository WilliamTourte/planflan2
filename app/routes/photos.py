"""Module des routes de gestion des photos de l'application PlanFlan.

Ce module gère le téléchargement et la gestion des photos,
otamment pour les établissements et les flans.
"""

from flask import (
    Flask,
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
        # Validez le fichier
        if file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            flash("Fichier téléversé avec succès!", "success")
            return redirect(url_for("photos.show_uploads"))
        else:
            flash("Fichier non valide. Veuillez téléverser une image.", "danger")
            return redirect(url_for("photos.show_uploads"))


@photos_bp.route("/uploads")
def show_uploads():
    uploads = os.listdir(current_app.config["UPLOAD_FOLDER"])
    return render_template("upload.html", uploads=uploads)
