"""Module des routes principales de l'application PlanFlan.

Ce module contient les routes principales de l'application, y compris
la page d'accueil, les pages de recherche, les pages d'établissements,
et les fonctionnalités principales accessibles aux utilisateurs.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    current_app,
    flash,
    make_response,
    jsonify,
)

from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.forms import (
    EvalForm,
    NewFlanForm,
    RechercheForm,
    UpdateProfileForm,
    EtabForm,
    DeleteForm,
    ValidateForm,
)
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app.models import Photo, TypeCible
from app import db, bcrypt
from app.outils import afficher_etablissements, calculer_distance, fetch_place_photos

main_bp = Blueprint("main", __name__)


## ROUTES PRINCIPALES
@main_bp.route("/")
def index():
    """Affiche la page d'accueil de l'application.

    Returns:
        Response: Page d'accueil avec la liste des établissements et formulaire de recherche
    """
    form_recherche = RechercheForm()
    etablissements = Etablissement.query.all()

    print(etablissements)

    return render_template(
        "index.html",
        etablissements=etablissements,
        etablissements_json=[etab.to_dict() for etab in etablissements],
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
        form_recherche=form_recherche,
    )


@main_bp.route("/api/villes")
def get_villes():
    """Route API pour récupérer les villes pour l'autocomplete"""
    search_term = request.args.get("q", "").lower()

    print(f"API /api/villes called with search_term: '{search_term}'")

    # Récupérer les villes qui correspondent à la recherche
    query = db.session.query(Etablissement.ville).distinct()
    if search_term:
        # Utilisation de paramètres sécurisés pour éviter les injections SQL
        search_pattern = f"%{search_term}%"
        query = query.filter(Etablissement.ville.ilike(search_pattern))

    villes = query.all()
    villes = [ville[0] for ville in villes if ville[0]]

    print(f"Found {len(villes)} villes: {villes[:5]}{'...' if len(villes) > 5 else ''}")

    return jsonify(sorted(villes))


def filtrer_etablissements(query, **kwargs):
    """Applique les filtres communs à une requête Etablissement."""
    if kwargs.get("nom"):
        # Utilisation de paramètres sécurisés pour éviter les injections SQL
        nom_pattern = f"%{kwargs['nom']}%"
        query = query.filter(Etablissement.nom.ilike(nom_pattern))
    if kwargs.get("ville"):
        # Utilisation de paramètres sécurisés pour éviter les injections SQL
        ville_pattern = f"%{kwargs['ville']}%"
        query = query.filter(Etablissement.ville.ilike(ville_pattern))
    if kwargs.get("visite") == "oui":
        query = query.filter(Etablissement.visite == True)
    elif kwargs.get("visite") == "non":
        query = query.filter(Etablissement.visite == False)
    if kwargs.get("labellise") == "oui":
        query = query.filter(Etablissement.label == True)
    elif kwargs.get("labellise") == "non":
        query = query.filter(Etablissement.label == False)
    if kwargs.get("type_pate") and kwargs["type_pate"] != "tous":
        query = query.filter(Flan.type_pate == kwargs["type_pate"])
    if kwargs.get("type_saveur") and kwargs["type_saveur"] != "tous":
        query = query.filter(Flan.type_saveur == kwargs["type_saveur"])
    if kwargs.get("type_texture") and kwargs["type_texture"] != "tous":
        query = query.filter(Flan.type_texture == kwargs["type_texture"])
    if kwargs.get("prix") and kwargs["prix"] != "tous":
        if kwargs["prix"] == "0":
            query = query.filter(Flan.prix < 2.5)
        elif kwargs["prix"] == "2.5":
            query = query.filter(Flan.prix >= 2.5, Flan.prix < 5)
        elif kwargs["prix"] == "5":
            query = query.filter(Flan.prix >= 5)
    return query


@main_bp.route("/liste_etablissements", methods=["GET", "POST"])
def liste_etablissements():


    # Détecter le mode géolocalisation
    geolocalisation_mode = (
        request.form.get("geolocalisation") == "true"
        or request.args.get("geolocalisation") == "true"
    )

    try:
        form_ajout = EtabForm(prefix="ajout-etab")
        form_edit = EtabForm(prefix="edit-etab")

        if request.method == "POST":
            form_recherche = RechercheForm(request.form)
        else:
           
            form_recherche = RechercheForm(request.args)

    except Exception as e:
        # En cas d'erreur avec les formulaires, créer des formulaires vides
        print(f"ERREUR FORMULAIRE: {str(e)}")
        form_ajout = EtabForm(prefix="ajout-etab")
        form_edit = EtabForm(prefix="edit-etab")
        form_recherche = RechercheForm()

    # 1. Recherche simple (GET uniquement) - MODIFIÉ pour ignorer en mode géolocalisation
    recherche_simple = request.args.get("recherche_simple", None)
    if recherche_simple and request.method == "GET" and not geolocalisation_mode:
        query = Etablissement.query.filter(
            (Etablissement.nom.ilike(f"%{recherche_simple}%"))
            | (Etablissement.ville.ilike(f"%{recherche_simple}%"))
        )
    else:
        query = Etablissement.query

    # 2. Nouvelle logique: toujours afficher tous les établissements
    # et utiliser le zoom JavaScript pour la ville sélectionnée
    ville_selectionnee = None

    # Récupérer la ville sélectionnée depuis les paramètres (GET ou POST)
    if request.method == "POST":
  
        if request.form.get("ville"):
            ville_selectionnee = request.form.get("ville")

    elif request.method == "GET":

        if request.args.get("ville"):
            ville_selectionnee = request.args.get("ville")


    # 3. Cas spécial: si on a des coordonnées mais pas de ville, on utilise les coordonnées pour le zoom
    user_lat = form_recherche.latitude.data
    user_lon = form_recherche.longitude.data

    if user_lat and user_lon and not ville_selectionnee:

        etablissements = query.distinct().all()
    else:
        # 4. Appliquer les autres filtres (sauf la ville)
        if (
            request.method == "POST"
            or form_recherche.validate_on_submit()
            or (request.method == "GET" and form_recherche.validate())
        ):
            # On ne fait la jointure que si un filtre sur Flan est activé
            need_join = (
                (
                    form_recherche.type_saveur.data
                    and form_recherche.type_saveur.data != "tous"
                )
                or (
                    form_recherche.type_pate.data
                    and form_recherche.type_pate.data != "tous"
                )
                or (
                    form_recherche.type_texture.data
                    and form_recherche.type_texture.data != "tous"
                )
                or (form_recherche.prix.data and form_recherche.prix.data != "tous")
            )
            if need_join:
                query = query.join(Flan)

            if form_recherche.nom.data:
                query = query.filter(
                    Etablissement.nom.ilike(f"%{form_recherche.nom.data}%")
                )

            if (
                form_recherche.type_saveur.data
                and form_recherche.type_saveur.data != "tous"
            ):
                query = query.filter(
                    Flan.type_saveur == form_recherche.type_saveur.data
                )
            if (
                form_recherche.type_pate.data
                and form_recherche.type_pate.data != "tous"
            ):
                query = query.filter(Flan.type_pate == form_recherche.type_pate.data)
            if (
                form_recherche.type_texture.data
                and form_recherche.type_texture.data != "tous"
            ):
                query = query.filter(
                    Flan.type_texture == form_recherche.type_texture.data
                )
            if form_recherche.prix.data and form_recherche.prix.data != "tous":
                if form_recherche.prix.data == "0":
                    query = query.filter(Flan.prix < 2.5)
                elif form_recherche.prix.data == "2.5":
                    query = query.filter(Flan.prix >= 2.5, Flan.prix < 5)
                elif form_recherche.prix.data == "5":
                    query = query.filter(Flan.prix >= 5)
            if form_recherche.visite.data and form_recherche.visite.data != "tous":
                query = query.filter(
                    Etablissement.visite == (form_recherche.visite.data == "oui")
                )
            if (
                form_recherche.labellise.data
                and form_recherche.labellise.data != "tous"
            ):
                query = query.filter(
                    Etablissement.label == (form_recherche.labellise.data == "oui")
                )

        etablissements = query.distinct().all()

    # 5. Préparation pour le template
    etablissements, etablissements_json = afficher_etablissements(etablissements)


    return render_template(
        "liste_etablissements.html",
        etablissements=etablissements,
        etablissements_json=etablissements_json,
        google_maps_api_key=current_app.config["GOOGLE_MAPS_API_KEY"],
        form_recherche=form_recherche,
        form_ajout=form_ajout,
        form_edit=form_edit,
        user_lat=user_lat,
        user_lon=user_lon,
        ville_selectionnee=ville_selectionnee,
    )


@main_bp.route("/api/etablissements", methods=["GET", "POST"])
def api_etablissements():
    try:
        # Récupère les paramètres de filtre
        if request.method == "POST":
            data = (
                request.get_json()
            )  # Récupère les données JSON envoyées avec la requête POST
            nom = data.get("nom", "")
            visite = data.get("visite", "")
            labellise = data.get("labellise", "")
            ville = data.get("ville", "")

            type_pate = data.get("type_pate", "tous")
            type_saveur = data.get("type_saveur", "tous")
            prix = data.get("prix", "tous")
            format = data.get("format", "json")  # 'html' ou 'json'
        else:
            nom = request.args.get("nom", "")
            visite = request.args.get("visite", "")
            labellise = request.args.get("labellise", "")
            ville = request.args.get("ville", "")

            type_pate = request.args.get("type_pate", "tous")
            type_saveur = request.args.get("type_saveur", "tous")
            prix = request.args.get("prix", "tous")
            format = request.args.get("format", "json")  # 'html' ou 'json'
        # Applique les filtres
        query = Etablissement.query.join(Flan)
        if nom:
            # Utilisation de paramètres sécurisés pour éviter les injections SQL
            nom_pattern = f"%{nom}%"
            query = query.filter(Etablissement.nom.ilike(nom_pattern))
        if visite == "oui":
            query = query.filter(Etablissement.visite == True)
        elif visite == "non":
            query = query.filter(Etablissement.visite == False)
        if labellise == "oui":
            query = query.filter(Etablissement.label == True)
        elif labellise == "non":
            query = query.filter(Etablissement.label == False)
        if ville:
            # Utilisation de paramètres sécurisés pour éviter les injections SQL
            ville_pattern = f"%{ville}%"
            query = query.filter(Etablissement.ville.ilike(ville_pattern))
        if type_pate != "tous":
            query = query.filter(Flan.type_pate == type_pate)
        if type_saveur != "tous":
            query = query.filter(Flan.type_saveur == type_saveur)
        if prix != "tous":
            if prix == "0":
                query = query.filter(Flan.prix < 2.5)
            elif prix == "2.5":
                query = query.filter(Flan.prix >= 2.5, Flan.prix < 5)
            elif prix == "5":
                query = query.filter(Flan.prix >= 5)
        # Récupère les résultats uniques
        etablissements = []
        seen = set()
        for etab in query.all():
            if etab.id_etab not in seen:
                seen.add(etab.id_etab)
                etablissements.append(etab)
        # Renvoie HTML ou JSON
        if format == "html":
            from flask import render_template_string

            # Utiliser une macro existante pour générer le HTML
            html_content = """
            {% from 'macros.html' import afficher_grille %}
            {{ afficher_grille('etablissement', etablissements, current_user=current_user) }}
            """
            html = render_template_string(
                html_content, etablissements=etablissements, current_user=current_user
            )
            response = make_response(html)
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            return response
        else:
            # Utilisez la méthode to_dict pour inclure les flans
            return jsonify([etab.to_dict() for etab in etablissements])
    except Exception as e:
        # En cas d'erreur, renvoie toujours du JSON avec un message d'erreur
        return jsonify({"error": str(e)}), 500


### INFOWINDOW
@main_bp.route("/get_infowindow_content")
def get_infowindow_content():
    id_etab = request.args.get("id_etab", type=int)
    etablissement = db.session.get(Etablissement, id_etab)
    if not etablissement:
        return "Détails non disponibles", 404

    details_url = url_for(
        "main.afficher_etablissement_unique", id_etab=etablissement.id_etab
    )
    return render_template(
        "infowindow_template.html", etablissement=etablissement, details_url=details_url
    )


### PAGE RECHERCHE
@main_bp.route("/rechercher", methods=["GET"])
def rechercher():
    try:
        form_recherche = RechercheForm()
    except Exception as e:
        print(f"ERREUR FORMULAIRE RECHERCHE: {str(e)}")
        form_recherche = RechercheForm()
    return render_template("rechercher.html", form_recherche=form_recherche)


### DASHBOARD
@main_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form_ajout = EtabForm()  # Instancie le formulaire
    profile_form = UpdateProfileForm(prefix="profile")
    eval_form = EvalForm(prefix="dashboard-eval")
    pending_evaluations = []
    pending_flans = []
    pending_etablissements = []
    if current_user.is_admin:
        pending_evaluations = (
            Evaluation.query.filter_by(statut="EN_ATTENTE")
            .join(Utilisateur)
            .filter(Utilisateur.is_admin == False)
            .all()
        )
        pending_flans = (
            Flan.query.filter_by(statut="EN_ATTENTE")
            .join(Utilisateur)
            .filter(Utilisateur.is_admin == False)
            .all()
        )
        pending_etablissements = (
            Etablissement.query.filter_by(statut="EN_ATTENTE")
            .join(Utilisateur)
            .filter(Utilisateur.is_admin == False)
            .all()
        )

    if request.method == "POST" and profile_form.validate_on_submit():
        if profile_form.email.data and profile_form.email.data != current_user.email:
            existing_user = Utilisateur.query.filter(
                Utilisateur.email == profile_form.email.data
            ).first()
            if existing_user and existing_user.id_user != current_user.id_user:
                flash("Cet email est déjà utilisé par un autre utilisateur.", "danger")
                return redirect(url_for("main.dashboard"))

        current_user.pseudo = profile_form.pseudo.data
        if profile_form.email.data:
            current_user.email = profile_form.email.data
        if profile_form.new_password.data:
            current_user.password = bcrypt.generate_password_hash(
                profile_form.new_password.data
            ).decode("utf-8")
        try:
            db.session.commit()
            flash("Votre profil a été mis à jour!", "success")
        except IntegrityError:
            db.session.rollback()
            flash(
                "Une erreur est survenue lors de la mise à jour de votre profil.",
                "danger",
            )
        return redirect(url_for("main.dashboard"))

    elif request.method == "GET":
        profile_form.pseudo.data = current_user.pseudo
        profile_form.email.data = current_user.email

    return render_template(
        "dashboard.html",
        title="Tableau de bord",
        form_ajout=form_ajout,
        profile_form=profile_form,
        eval_form=eval_form,
        pending_evaluations=pending_evaluations,
        pending_flans=pending_flans,
        pending_etablissements=pending_etablissements,
    )


### Routes établissement, flan, évaluation
@main_bp.route("/etablissement/<int:id_etab>", methods=["GET", "POST"])
def afficher_etablissement_unique(id_etab):
    etablissement = db.session.get(Etablissement, id_etab)
    if etablissement is None:
        from flask import abort

        abort(404)
    form_etab = EtabForm(prefix="edit-etab", obj=etablissement)
    delete_form = DeleteForm()
    validate_form = ValidateForm()
    form_flan = NewFlanForm(prefix="ajout-flan")

    # Récupérer ou télécharger les photos pour l'établissement
    photo_paths = fetch_place_photos(
        id_etab,
        etablissement.google_place_id,
        current_app.config["GOOGLE_MAPS_API_KEY"],
    )

    if form_etab.validate_on_submit():
        etablissement.nom = form_etab.nom.data
        etablissement.description = form_etab.description.data
        etablissement.adresse = form_etab.adresse.data
        etablissement.ville = form_etab.ville.data
        etablissement.code_postal = form_etab.code_postal.data
        etablissement.latitude = form_etab.latitude.data
        etablissement.longitude = form_etab.longitude.data
        etablissement.type_etab = form_etab.type_etab.data
        if current_user.is_admin:
            etablissement.label = form_etab.label.data
            etablissement.visite = form_etab.visite.data
        db.session.commit()
        flash("L'établissement a été mis à jour avec succès!", "success")
        return redirect(url_for("main.afficher_etablissement_unique", id_etab=id_etab))

    return render_template(
        "page_etablissement.html",
        etablissement=etablissement,
        form_flan=form_flan,
        form_etab=form_etab,
        current_user=current_user,
        delete_form=delete_form,
        validate_form=validate_form,
        photo_paths=photo_paths,
    )


@main_bp.route("/flan/<int:id_flan>", methods=["GET", "POST"])
def afficher_flan_unique(id_flan):
    flan_unique = db.session.get(Flan, id_flan)
    if flan_unique is None:
        from flask import abort

        abort(404)
    form_eval = EvalForm(prefix="flan-eval")
    form_flan = NewFlanForm(prefix="edit-flan", obj=flan_unique)
    delete_form = DeleteForm()
    validate_form = ValidateForm()

    # Traitement de la soumission du formulaire d'édition du flan
    if form_flan.validate_on_submit():
        flan_unique.nom = form_flan.nom.data
        flan_unique.description = form_flan.description.data
        flan_unique.prix = form_flan.prix.data
        flan_unique.type_pate = form_flan.type_pate.data
        flan_unique.type_saveur = form_flan.type_saveur.data
        flan_unique.type_texture = form_flan.type_texture.data
        db.session.commit()
        flash("Le flan a été mis à jour avec succès!", "success")
        return redirect(url_for("main.afficher_flan_unique", id_flan=id_flan))

    return render_template(
        "page_flan.html",
        flan=flan_unique,
        form_eval=form_eval,
        form_flan=form_flan,
        current_user=current_user,
        delete_form=delete_form,
        validate_form=validate_form,
    )


@main_bp.route("/etablissement/<int:id_etab>/proposer_flan", methods=["GET", "POST"])
@login_required
def proposer_flan(id_etab):
    etablissement = db.session.get(Etablissement, id_etab)
    if etablissement is None:
        from flask import abort

        abort(404)
    form = NewFlanForm(prefix="ajout-flan")
    form.id_etab.data = id_etab
    if form.validate_on_submit():
        flan = Flan(
            nom=form.nom.data,
            description=form.description.data,
            prix=form.prix.data,
            type_pate=form.type_pate.data,
            type_saveur=form.type_saveur.data,
            type_texture=form.type_texture.data,
            id_etab=id_etab,
            id_user=current_user.id_user,
        )
        db.session.add(flan)
        db.session.commit()
        flash("Votre flan a été proposé avec succès !", "success")
        return redirect(url_for("main.afficher_etablissement_unique", id_etab=id_etab))
    return render_template(
        "page_etablissement.html", form=form, etablissement=etablissement
    )


@main_bp.route("/valider_flan/<int:id_flan>", methods=["POST"])
@login_required
def valider_flan(id_flan):
    if not current_user.is_admin:
        flash("Vous n'avez pas le droit d'accéder à cette page.", "danger")
        return redirect(url_for("main.dashboard"))
    flan = db.session.get(Flan, id_flan)
    if flan is None:
        from flask import abort

        abort(404)
    flan.statut = "VALIDE"
    try:
        db.session.commit()
        flash("Le flan a été validé avec succès!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Une erreur est survenue lors de la validation du flan.", "danger")
    return redirect(url_for("main.afficher_flan_unique", id_flan=id_flan))


@main_bp.route("/modifier_flan/<int:id_flan>", methods=["POST"])
@login_required
def modifier_flan(id_flan):
    flan = db.session.get(Flan, id_flan)
    if flan is None:
        from flask import abort

        abort(404)
    form = NewFlanForm(prefix="edit-flan")
    if current_user.id_user != flan.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de modifier ce flan.", "danger")
        return redirect(url_for("main.afficher_flan_unique", id_flan=id_flan))
    if form.validate_on_submit():
        flan.nom = form.nom.data
        flan.type_saveur = form.type_saveur.data
        flan.type_texture = form.type_texture.data
        flan.type_pate = form.type_pate.data
        flan.description = form.description.data
        flan.prix = form.prix.data
        db.session.commit()
        flash("Le flan a été mis à jour avec succès!", "success")
    else:
        flash(
            "Le formulaire n'a pas été validé. Veuillez vérifier les erreurs.", "danger"
        )
    return redirect(url_for("main.afficher_flan_unique", id_flan=id_flan))


@main_bp.route("/supprimer_flan/<int:id_flan>", methods=["POST"])
@login_required
def supprimer_flan(id_flan):
    flan = db.session.get(Flan, id_flan)
    if flan is None:
        from flask import abort

        abort(404)
    if current_user.id_user != flan.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de supprimer ce flan.", "danger")
        return redirect(url_for("main.dashboard"))
    db.session.delete(flan)
    try:
        db.session.commit()
        flash("Le flan a été supprimé avec succès!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Une erreur est survenue lors de la suppression du flan.", "danger")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/flan/<int:id_flan>/evaluer", methods=["GET", "POST"])
@login_required
def evaluer_flan(id_flan):

    form = EvalForm(prefix="flan-eval")
    evaluation = Evaluation.query.filter_by(
        id_flan=id_flan, id_user=current_user.id_user
    ).first()
    if request.method == "GET" and evaluation:
        form.visuel.data = str(evaluation.visuel)
        form.texture.data = str(evaluation.texture)
        form.pate.data = str(evaluation.pate)
        form.gout.data = str(evaluation.gout)
        form.description.data = evaluation.description
    if form.validate_on_submit():
        try:
            evaluation = mise_a_jour_evaluation(
                form, id_flan, current_user.id_user, current_user.is_admin
            )
            flash("Votre évaluation a été mise à jour avec succès!", "success")
        except Exception as e:
            print("Error during form submission:", e)
            flash(
                "Une erreur est survenue lors de la mise à jour de l'évaluation: "
                + str(e),
                "danger",
            )
    else:
        if request.method == "POST":
            print("Form validation errors:", form.errors)
            flash(
                "Le formulaire n'a pas été validé correctement. Veuillez vérifier les erreurs.",
                "danger",
            )
    return redirect(url_for("main.afficher_flan_unique", id_flan=id_flan))


@main_bp.route("/evaluation/<int:id_eval>", methods=["GET", "POST"])
@login_required
def afficher_evaluation_unique(id_eval):
    evaluation = db.session.get(Evaluation, id_eval)
    if evaluation is None:
        from flask import abort

        abort(404)
    flan_unique = db.session.get(Flan, evaluation.id_flan)
    if flan_unique is None:
        from flask import abort

        abort(404)
    form = EvalForm(prefix="eval-detail")
    delete_form = DeleteForm()
    validate_form = ValidateForm()

    if request.method == "GET":
        form.visuel.data = evaluation.visuel
        form.texture.data = evaluation.texture
        form.pate.data = evaluation.pate
        form.gout.data = evaluation.gout
        form.description.data = evaluation.description
    if form.validate_on_submit():
        evaluation = mise_a_jour_evaluation(
            form, flan_unique.id_flan, current_user.id_user, current_user.is_admin
        )
        flash("L'évaluation a été mise à jour avec succès!", "success")
        return redirect(
            url_for("main.afficher_evaluation_unique", id_eval=evaluation.id_eval)
        )
    return render_template(
        "page_evaluation.html",
        evaluation=evaluation,
        form=form,
        current_user=current_user,
        delete_form=delete_form,  # <-- Passe delete_form au template
        validate_form=validate_form,
        current_page="page_evaluation",
    )


def mise_a_jour_evaluation(form, id_flan, id_user, is_admin=False):
    print("Form data received:", form.data)
    visuel = (
        float(str(form.visuel.data).replace(",", "."))
        if form.visuel.data is not None
        else None
    )
    texture = (
        float(str(form.texture.data).replace(",", "."))
        if form.texture.data is not None
        else None
    )
    pate = (
        float(str(form.pate.data).replace(",", "."))
        if form.pate.data is not None
        else None
    )
    gout = (
        float(str(form.gout.data).replace(",", "."))
        if form.gout.data is not None
        else None
    )
    description = form.description.data if form.description.data is not None else ""

    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=id_user).first()
    if evaluation:
        # Toujours mettre à jour tous les champs, même s'ils n'ont pas changé
        evaluation.visuel = visuel
        evaluation.texture = texture
        evaluation.pate = pate
        evaluation.gout = gout
        evaluation.description = description
        moyenne = (
            float(evaluation.visuel or 0)
            + float(evaluation.texture or 0)
            + float(evaluation.pate or 0)
            + float(evaluation.gout or 0)
        ) / 4
        evaluation.moyenne = moyenne
    else:
        moyenne = (
            float(visuel or 0)
            + float(texture or 0)
            + float(pate or 0)
            + float(gout or 0)
        ) / 4
        evaluation = Evaluation(
            visuel=visuel,
            texture=texture,
            pate=pate,
            gout=gout,
            description=description,
            id_flan=id_flan,
            id_user=id_user,
            moyenne=moyenne,
        )
    if is_admin:
        evaluation.statut = "VALIDE"
    db.session.add(evaluation)
    db.session.commit()
    return evaluation


@main_bp.route("/valider_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def valider_evaluation(id_eval):
    if not current_user.is_admin:
        flash("Vous n'avez pas le droit d'accéder à cette page.", "danger")
        return redirect(url_for("main.dashboard"))
    evaluation = db.session.get(Evaluation, id_eval)
    if evaluation is None:
        from flask import abort

        abort(404)
    evaluation.statut = "VALIDE"
    try:
        db.session.commit()
        flash("L'évaluation a été validée avec succès!", "success")
    except IntegrityError:
        db.session.rollback()
        flash(
            "Une erreur est survenue lors de la validation de l'évaluation.", "danger"
        )
    return redirect(url_for("main.dashboard"))


@main_bp.route("/supprimer_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def supprimer_evaluation(id_eval):
    evaluation = db.session.get(Evaluation, id_eval)
    if evaluation is None:
        from flask import abort

        abort(404)
    if current_user.id_user != evaluation.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de supprimer cette évaluation.", "danger")
        return redirect(url_for("main.dashboard"))
    db.session.delete(evaluation)
    try:
        db.session.commit()
        flash("L'évaluation a été supprimée avec succès!", "success")
    except IntegrityError:
        db.session.rollback()
        flash(
            "Une erreur est survenue lors de la suppression de l'évaluation.", "danger"
        )
    return redirect(url_for("main.dashboard"))


### BADGES
def afficher_badge_etablissement(etablissement):
    if hasattr(etablissement, "label") and etablissement.label:
        return '<span class="badge badge-labellise">❤️</span>'
    return ""


def afficher_badge_type_etab(etablissement):
    couleurs = {
        "BOULANGERIE": "#F5DEB3",
        "PATISSERIE": "#FFB6C1",
        "RESTAURANT": "#87CEEB",
        "CAFE": "#D2B48C",
    }
    type_etab = getattr(etablissement, "type_etab", None)
    if type_etab:
        couleur = couleurs.get(type_etab.name, "#D3D3D3")
        return f'<div class="badge badge-type-etab" style="background-color: {couleur};">{type_etab.value}</div>'
    return ""
