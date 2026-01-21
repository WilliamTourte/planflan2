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
        return jsonify({"error": str(e)}), 500


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
    current_app.logger.info("=== DEBUT ajouter_etablissement ===")
    form_ajout = EtabForm(prefix="ajout-etab")
    if request.method == "POST":
        current_app.logger.info(f"Méthode POST reçue")
        current_app.logger.info(f"Tous les champs de la requête: {dict(request.form)}")

        # Vérification du google_place_id dans la requête
        # Ce champ est utilisé pour récupérer les photos depuis Google Places
        if "ajout-etab-google_place_id" in request.form:
            google_place_id_from_request = request.form["ajout-etab-google_place_id"]
            current_app.logger.info(
                f"✓ google_place_id trouvé dans la requête: '{google_place_id_from_request}' (longueur: {len(google_place_id_from_request)})"
            )
        else:
            current_app.logger.error("✗ google_place_id NON TROUVÉ dans la requête")
            current_app.logger.info(f"Champs disponibles: {list(request.form.keys())}")

        form_ajout = EtabForm(prefix="ajout-etab", formdata=MultiDict(request.form))

        current_app.logger.info(
            f"Formulaire créé, google_place_id.data: '{form_ajout.google_place_id.data}' (type: {type(form_ajout.google_place_id.data)})"
        )

        # Validation du formulaire et création de l'établissement
        # Si le formulaire est valide, les données sont utilisées pour créer un nouvel établissement
        if form_ajout.validate():
            current_app.logger.info("✓ Formulaire validé avec succès")
            current_app.logger.info("=== CRÉATION DE L'ÉTABLISSEMENT ===")
            current_app.logger.info(f"Valeurs utilisées pour la création:")
            current_app.logger.info(f"  nom: {form_ajout.nom.data}")
            current_app.logger.info(
                f"  google_place_id: '{form_ajout.google_place_id.data}' (type: {type(form_ajout.google_place_id.data)})"
            )

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
                google_place_id=form_ajout.google_place_id.data,
            )

            current_app.logger.info(
                f"Établissement créé en mémoire, google_place_id: '{nouvel_etablissement.google_place_id}'"
            )

            db.session.add(nouvel_etablissement)
            current_app.logger.info("Établissement ajouté à la session")

            db.session.commit()
            current_app.logger.info("Transaction commitée")

            # Récupère l'ID de l'établissement nouvellement créé
            id_etab = nouvel_etablissement.id_etab
            current_app.logger.info(f"ID de l'établissement créé: {id_etab}")

            # Vérification en base de données
            etablissement_verif = db.session.get(Etablissement, id_etab)
            current_app.logger.info(
                f"Vérification en base - google_place_id: '{etablissement_verif.google_place_id}'"
            )

            # Télécharger les photos depuis Google Places si un place_id est disponible
            current_app.logger.info(
                f"Google Place ID de l'établissement créé: '{nouvel_etablissement.google_place_id}' (type: {type(nouvel_etablissement.google_place_id)})"
            )
            if nouvel_etablissement.google_place_id:
                try:
                    from app.outils import fetch_place_photos

                    current_app.logger.info(
                        f"Appel de fetch_place_photos avec id_etab={id_etab}, place_id='{nouvel_etablissement.google_place_id}'"
                    )
                    fetch_place_photos(
                        id_etab,
                        nouvel_etablissement.google_place_id,
                        current_app.config["GOOGLE_MAPS_API_KEY"],
                    )
                    current_app.logger.info(
                        "Téléchargement des photos Google Places terminé"
                    )
                except Exception as e:
                    current_app.logger.error(
                        f"Erreur lors du téléchargement des photos Google Places: {str(e)}"
                    )
                    current_app.logger.error(traceback.format_exc())
                    # Ne pas échouer la création de l'établissement si les photos ne peuvent pas être téléchargées
            else:
                current_app.logger.warning(
                    "⚠️  Aucun Google Place ID disponible, pas de téléchargement de photos"
                )

            flash("Établissement ajouté avec succès !", "success")
            current_app.logger.info(
                f"=== FIN ajouter_etablissement - Redirection vers id_etab={id_etab} ==="
            )
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
    etablissement = db.session.get(Etablissement, id_etab)
    if etablissement is None:
        from flask import abort

        abort(404)

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
            return redirect(
                url_for("main.afficher_etablissement_unique", id_etab=id_etab)
            )

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
    etablissement = db.session.get(Etablissement, id_etab)
    if etablissement is None:
        from flask import abort

        abort(404)

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
    etablissement = db.session.get(Etablissement, id_etab)
    if etablissement is None:
        from flask import abort

        abort(404)

    # Vérifier si l'utilisateur est l'auteur de l'établissement ou un admin
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de supprimer cet établissement.", "error")
        return redirect(url_for("main.index"))

    # Supprimer l'établissement de la base de données
    db.session.delete(etablissement)
    db.session.commit()
    flash("Établissement supprimé avec succès !", "success")
    return redirect(url_for("main.index"))
