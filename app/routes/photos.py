from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    current_app,
)
import os
from werkzeug.utils import secure_filename

photos_bp = Blueprint("photos", __name__)


@photos_bp.route("/upload", methods=["POST"])
def upload_file():
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
            return redirect(url_for("photos.show_uploads"))
        else:
            return "Fichier non valide. Veuillez téléverser une image."


@photos_bp.route("/uploads")
def show_uploads():
    uploads = os.listdir(current_app.config["UPLOAD_FOLDER"])
    return render_template("upload.html", uploads=uploads)
