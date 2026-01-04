"""Module des routes de cartes et géolocalisation de l'application PlanFlan.

Ce module gère les fonctionnalités liées aux cartes, à la géolocalisation
et à la gestion des établissements sur les cartes interactives.
"""

import traceback
from werkzeug.datastructures import MultiDict
from app.outils import afficher_etablissements, calculer_distance
import re

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    current_app,
    flash,
    jsonify,
)
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf

from app.forms import EtabForm
from app.models import Etablissement, TypeEtab
from app import db
from app.outils import verifier_csrf_ou_renvoyer_erreur

maps_bp = Blueprint("maps", __name__)


def extraire_code_postal(adresse):
    match = re.search(r"(\d{5})", adresse)
    return match.group(1) if match else None


def extraire_ville(adresse):
    """Extrait le nom de la ville à partir d'une adresse complète.

    Args:
        adresse (str): L'adresse complète contenant le code postal et la ville

    Returns:
        str: Le nom de la ville extrait, ou None si non trouvé
    """
    match = re.search(r"\d{5}\s+([^,]+)", adresse)
    return match.group(1).strip() if match else None


def nettoyer_adresse(adresse):
    """Nettoie une adresse en ne gardant que la partie principale.

    Args:
        adresse (str): L'adresse complète à nettoyer

    Returns:
        str: La partie principale de l'adresse (avant la première virgule)
    """
    return adresse.split(",")[0].strip()


@maps_bp.route("/geoloc", methods=["POST"])
def geoloc():
    """Gère la réception des données de géolocalisation.

    Cette route reçoit les données GPS envoyées par le navigateur
    et les traite pour mettre à jour la position de l'utilisateur.

    Returns:
        Response: JSON avec confirmation ou erreur
    """
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
    if not csrf_valide:
        return response

    try:
        data = request.get_json()

        if not data:
            print("Données GPS non reçues")
            return jsonify({"error": "Données GPS non reçues"}), 400
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        return jsonify(
            {"status": "success", "latitude": latitude, "longitude": longitude}
        )
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@maps_bp.route("/etablissements_proches", methods=["POST"])
def etablissements_proches():
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
    if not csrf_valide:
        return response

    try:
        data = request.get_json()
        user_lat = data["latitude"]
        user_lon = data["longitude"]
        rayon_km = 5  # Rayon en kilomètres

        # Récupère tous les établissements depuis la base
        etablissements = Etablissement.query.all()

        # Filtre les établissements dans le rayon de 5 km
        etablissements_proches_liste = []
        for etab in etablissements:
            distance = calculer_distance(
                user_lat, user_lon, etab.latitude, etab.longitude
            )
            if distance <= rayon_km:
                etablissements_proches_liste.append(
                    {
                        "id_etab": etab.id_etab,
                        "nom": etab.nom,
                        "adresse": etab.adresse,
                        "latitude": etab.latitude,
                        "longitude": etab.longitude,
                        "distance": round(distance, 2),  # Arrondi à 2 décimales
                        "visite": etab.visite,
                        "label": etab.label,
                    }
                )

        return jsonify({"etablissements": etablissements_proches_liste})

    except Exception as e:
        current_app.logger.error(f"Erreur : {str(e)}")
        return jsonify({"error": str(e)}), 500


@maps_bp.route("/extraire_infos_adresse", methods=["POST"])
def extraire_infos_adresse():
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
    if not csrf_valide:
        return response

    try:
        data = request.get_json()
        if not data or "adresse" not in data:
            return jsonify({"error": "Adresse manquante"}), 400
        adresse = data["adresse"]
        code_postal = extraire_code_postal(adresse)
        ville = extraire_ville(adresse)
        adresse_nettoyee = nettoyer_adresse(adresse)
        return jsonify(
            {
                "code_postal": code_postal,
                "ville": ville,
                "adresse_nettoyee": adresse_nettoyee,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@maps_bp.route("/proposer_etablissement", methods=["GET", "POST"])
def proposer_etablissement():
    form = EtabForm(prefix="ajout-etab")  # Ajoute le préfixe ici
    return render_template(
        "proposer_etablissement.html",
        action_url=url_for("maps.ajouter_etablissement"),
        form=form,
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
    )


@maps_bp.route("/verifier_etablissement", methods=["POST"])
def verifier_etablissement():
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
    if not csrf_valide:
        return response

    try:
        data = request.get_json()
        if not data or "nom" not in data:
            current_app.logger.error("Données manquantes ou mal formatées")
            return jsonify({"error": "Le nom de l'établissement est requis"}), 400

        nom = data["nom"]
        if not nom or not nom.strip():
            return jsonify({"error": "Le nom ne peut pas être vide"}), 400

        etablissement = Etablissement.query.filter_by(nom=nom).first()
        if etablissement:
            current_app.logger.info(f"Établissement trouvé : {etablissement.nom}")
            return jsonify(
                {
                    "exists": True,
                    "url": url_for(
                        "main.afficher_etablissement_unique",
                        id_etab=etablissement.id_etab,
                        _external=True,
                    ),
                    "id_etab": etablissement.id_etab,
                }
            )
        else:
            current_app.logger.info("Aucun établissement trouvé avec ce nom.")
            return jsonify({"exists": False})

    except Exception as e:
        current_app.logger.error(f"Erreur serveur: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Une erreur est survenue côté serveur"}), 500


@maps_bp.route("/ajouter_etablissement", methods=["GET", "POST"])
def ajouter_etablissement():
    form_ajout = EtabForm(prefix="ajout-etab")
    if request.method == "POST":
        form_ajout = EtabForm(prefix="ajout-etab", formdata=MultiDict(request.form))
        if form_ajout.validate():
            nouvel_etablissement = Etablissement(
                nom=form_ajout.nom.data,
                adresse=form_ajout.adresse.data,
                code_postal=form_ajout.code_postal.data,
                ville=form_ajout.ville.data,
                latitude=form_ajout.latitude.data,
                longitude=form_ajout.longitude.data,
                type_etab=form_ajout.type_etab.data,
                description=form_ajout.description.data,
                id_user=1,  # TEMPORAIRE
                label=form_ajout.label.data,
                visite=form_ajout.visite.data,
            )
            db.session.add(nouvel_etablissement)
            db.session.commit()

            # Récupère l'ID de l'établissement nouvellement créé
            id_etab = nouvel_etablissement.id_etab

            flash("Établissement ajouté avec succès !", "success")
            # Redirige vers la page de l'établissement
            return redirect(
                url_for("main.afficher_etablissement_unique", id_etab=id_etab)
            )

        else:
            print("\n9. ERREURS DE VALIDATION:")
            for field_name, errors in form_ajout.errors.items():
                print(f"   {field_name}: {errors}")

    # Pour une requête GET (ne devrait pas servir)
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template(
        "liste_etablissements.html",
        etablissements=etablissements,
        etablissements_json=etablissements_json,
        form_ajout=form_ajout,
        form_edit=EtabForm(prefix="edit-etab"),
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
    )


@maps_bp.route("/modifier_etablissement/<int:id_etab>", methods=["GET", "POST"])
@login_required
def modifier_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Instanciation des formulaires avec leurs préfixes respectifs
    form_edit = EtabForm(prefix="edit-etab")
    form_ajout = EtabForm(prefix="ajout-etab")

    # Définition des choix pour les deux formulaires
    form_edit.type_etab.choices = [
        (type_etab.name, type_etab.value) for type_etab in TypeEtab
    ]
    form_ajout.type_etab.choices = [
        (type_etab.name, type_etab.value) for type_etab in TypeEtab
    ]

    # Vérification des droits
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de modifier cet établissement.", "error")
        return redirect(url_for("main.index"))

    if request.method == "GET":
        # Pré-remplissage du formulaire d'édition
        form_edit.nom.data = etablissement.nom
        form_edit.adresse.data = etablissement.adresse
        form_edit.code_postal.data = etablissement.code_postal
        form_edit.ville.data = etablissement.ville
        form_edit.latitude.data = etablissement.latitude
        form_edit.longitude.data = etablissement.longitude
        form_edit.type_etab.data = etablissement.type_etab.name
        form_edit.label.data = "Oui" if etablissement.label else "Non"
        form_edit.visite.data = "Oui" if etablissement.visite else "Non"
        form_edit.description.data = etablissement.description

    elif request.method == "POST":
        # Recréation du formulaire d'édition avec les données POST
        form_edit = EtabForm(prefix="edit-etab", formdata=request.form)
        if form_edit.validate_on_submit():
            # Mise à jour des données de l'établissement
            etablissement.nom = form_edit.nom.data
            etablissement.adresse = form_edit.adresse.data
            etablissement.code_postal = form_edit.code_postal.data
            etablissement.ville = form_edit.ville.data
            etablissement.latitude = (
                form_edit.latitude.data
            )  # Utilisation de form_edit au lieu de request.form
            etablissement.longitude = (
                form_edit.longitude.data
            )  # Utilisation de form_edit au lieu de request.form
            etablissement.type_etab = TypeEtab[form_edit.type_etab.data]
            etablissement.label = form_edit.label.data == "Oui"
            etablissement.visite = form_edit.visite.data == "Oui"
            etablissement.description = form_edit.description.data
            db.session.commit()
            flash("Établissement mis à jour avec succès !", "success")
            return redirect(url_for("main.index"))

    # Récupération de tous les établissements pour l'affichage
    etablissements = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(etablissements)

    # Rendement du template avec tous les éléments nécessaires
    return render_template(
        "liste_etablissements.html",
        form_edit=form_edit,  # Formulaire d'édition pré-rempli
        form_ajout=form_ajout,  # Formulaire d'ajout vide
        etablissements_json=etablissements_json,
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
    )


@maps_bp.route("/valider_etablissement/<int:id_etab>", methods=["POST"])
@login_required
def valider_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Vérifier si l'utilisateur est un admin
    if not current_user.is_admin:
        flash("Vous n'avez pas le droit de valider cet établissement.", "error")
        return redirect(url_for("main.index"))

    # Mettre à jour le statut de l'établissement
    etablissement.statut = "VALIDE"
    db.session.commit()
    flash("Établissement validé avec succès !", "success")
    return redirect(url_for("main.index"))


@maps_bp.route("/supprimer_etablissement/<int:id_etab>", methods=["POST"])
@login_required
def supprimer_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Vérifier si l'utilisateur est l'auteur de l'établissement ou un admin
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de supprimer cet établissement.", "error")
        return redirect(url_for("main.index"))

    # Supprimer l'établissement de la base de données
    db.session.delete(etablissement)
    db.session.commit()
    flash("Établissement supprimé avec succès !", "success")
    return redirect(url_for("main.index"))
