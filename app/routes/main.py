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
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
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
        Response: Page d'accueil avec formulaire de recherche
    """
    form_recherche = RechercheForm()

    return render_template(
        "index.html",
        form_recherche=form_recherche,
    )


@main_bp.route("/api/villes")
def get_villes():
    """Route API pour récupérer les villes pour l'autocomplete

    Version optimisée utilisant les données statiques au lieu des requêtes SQL.

    Paramètres:
        q: Terme de recherche pour les villes
        with_gps: Si présent, retourne aussi les coordonnées GPS (format: "nom|lat|lng")
    """
    search_term = request.args.get("q", "").lower()
    with_gps = request.args.get("with_gps", "").lower() in ("true", "1", "yes")

    # Utiliser les données statiques directement
    try:
        import json
        import os

        # Charger les données une seule fois (cache au niveau du module)
        if not hasattr(get_villes, "villes_cache"):
            # Charger le fichier avec les données de population
            autocomplete_file = os.path.join(
                current_app.root_path, "..", "app", "data", "villes_autocomplete.json"
            )
            with open(autocomplete_file, "r", encoding="utf-8") as f:
                get_villes.villes_cache = json.load(f)
                print(f"Loaded {len(get_villes.villes_cache)} villes from static file")

        # Recherche ultra-rapide dans la liste statique
        if search_term:
            results = [
                ville
                for ville in get_villes.villes_cache
                if search_term in ville["nom"].lower()
            ]
        else:
            results = get_villes.villes_cache[:]  # Copier toutes les villes

        # Trier les résultats par population décroissante
        results.sort(key=lambda x: x.get("population", 0), reverse=True)

        # Limiter à 20 résultats
        results = results[:20]

        # Formater les résultats selon le paramètre with_gps
        if with_gps:
            # Retourner les noms avec les coordonnées GPS (format: "nom|latitude|longitude")
            formatted_results = [
                f"{ville['nom']}|{ville['latitude']}|{ville['longitude']}"
                for ville in results
            ]

            return jsonify(formatted_results)
        else:
            # Retourner seulement les noms (pour la compatibilité)
            simple_results = [ville["nom"] for ville in results]

            return jsonify(simple_results)

    except Exception as e:
        print(f"Error loading static data: {e}")
        # En cas d'erreur, tomber en secours sur l'ancienne méthode
        print("Falling back to database query...")
        query = db.session.query(Etablissement.ville).distinct()
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(Etablissement.ville.ilike(search_pattern))

        villes = query.all()
        villes = [ville[0] for ville in villes if ville[0]]

        return jsonify(sorted(villes))


def extraire_parametres_filtre(source=None, request=None, form=None):
    """Extraire les paramètres de filtre depuis différentes sources.

    Args:
        source: 'get', 'post', ou None (pour utiliser form)
        request: Objet request Flask (pour GET/POST)
        form: Formulaire Flask (pour les routes avec formulaire)

    Returns:
        dict: Paramètres de filtre prêts pour filtrer_etablissements
    """
    filtres = {}

    if source == "post" and request:
        data = request.get_json() or {}
        filtres["nom"] = data.get("nom", "")
        filtres["visite"] = data.get("visite", "")
        filtres["labellise"] = data.get("labellise", "")
        filtres["ville"] = data.get("ville", "")
        filtres["type_pate"] = data.get("type_pate", "tous")
        filtres["type_saveur"] = data.get("type_saveur", "tous")
        filtres["prix"] = data.get("prix", "tous")

    elif source == "get" and request:
        filtres["nom"] = request.args.get("nom", "")
        filtres["visite"] = request.args.get("visite", "")
        filtres["labellise"] = request.args.get("labellise", "")
        filtres["ville"] = request.args.get("ville", "")
        filtres["type_pate"] = request.args.get("type_pate", "tous")
        filtres["type_saveur"] = request.args.get("type_saveur", "tous")
        filtres["prix"] = request.args.get("prix", "tous")

    elif form:
        # Pour les routes avec formulaire comme /liste_etablissements
        if form.nom.data:
            filtres["nom"] = form.nom.data
        if form.visite.data and form.visite.data != "tous":
            filtres["visite"] = form.visite.data
        if form.labellise.data and form.labellise.data != "tous":
            filtres["labellise"] = form.labellise.data
        if form.type_saveur.data and form.type_saveur.data != "tous":
            filtres["type_saveur"] = form.type_saveur.data
        if form.type_pate.data and form.type_pate.data != "tous":
            filtres["type_pate"] = form.type_pate.data
        if form.type_texture.data and form.type_texture.data != "tous":
            filtres["type_texture"] = form.type_texture.data
        if form.prix.data and form.prix.data != "tous":
            filtres["prix"] = form.prix.data

    # Nettoyer les valeurs vides
    return {k: v for k, v in filtres.items() if v}


def extraire_parametres_filtre_api(request):
    """Version spécifique pour l'API qui gère à la fois GET et POST."""
    if request.method == "POST":
        return extraire_parametres_filtre(source="post", request=request)
    else:
        return extraire_parametres_filtre(source="get", request=request)


def filtrer_etablissements(query, **kwargs):
    """Applique les filtres communs à une requête Etablissement."""
    # Filtres sur Etablissement
    if kwargs.get("nom"):
        query = query.filter(Etablissement.nom.ilike(f"%{kwargs['nom']}%"))
    if kwargs.get("ville"):
        query = query.filter(Etablissement.ville.ilike(f"%{kwargs['ville']}%"))

    # Filtres booléens
    # Correction: le champ s'appelle 'label' et non 'labellise'
    if kwargs.get("visite") == "oui":
        query = query.filter(Etablissement.visite == True)
    elif kwargs.get("visite") == "non":
        query = query.filter(Etablissement.visite == False)

    # Accepter à la fois 'label' et 'labellise' comme paramètres pour la compatibilité
    labellise_value = kwargs.get("labellise") or kwargs.get("label")
    if labellise_value == "oui":
        query = query.filter(Etablissement.label == True)
    elif labellise_value == "non":
        query = query.filter(Etablissement.label == False)

    # Filtres sur Flan (nécessite une jointure)
    flan_filters = {
        "type_pate": kwargs.get("type_pate"),
        "type_saveur": kwargs.get("type_saveur"),
        "type_texture": kwargs.get("type_texture"),
        "prix": kwargs.get("prix"),
    }

    # Vérifier si au moins un filtre Flan est présent et différent de "tous"
    if any(v and v != "tous" for v in flan_filters.values()):
        # Vérifier si la requête est déjà jointe avec Flan pour éviter les ambiguïtés
        # Convertir la requête en chaîne pour vérifier si elle contient déjà une jointure
        query_str = str(query)
        if "JOIN" not in query_str.upper() and "INNER JOIN" not in query_str.upper():
            # Jointure explicite pour éviter les ambiguïtés
            query = query.join(Flan, Etablissement.flans)

        if flan_filters["type_pate"] and flan_filters["type_pate"] != "tous":
            query = query.filter(Flan.type_pate == flan_filters["type_pate"])
        if flan_filters["type_saveur"] and flan_filters["type_saveur"] != "tous":
            query = query.filter(Flan.type_saveur == flan_filters["type_saveur"])
        if flan_filters["type_texture"] and flan_filters["type_texture"] != "tous":
            query = query.filter(Flan.type_texture == flan_filters["type_texture"])

        # Gestion du filtre prix
        prix_mapping = {"0": (None, 2.5), "2.5": (2.5, 5), "5": (5, None)}
        if flan_filters["prix"] and flan_filters["prix"] in prix_mapping:
            min_prix, max_prix = prix_mapping[flan_filters["prix"]]
            if min_prix is not None:
                query = query.filter(Flan.prix >= min_prix)
            if max_prix is not None:
                query = query.filter(Flan.prix < max_prix)

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

    # toujours chercher tous les établissements
    query = Etablissement.query

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

    # Nouvelle logique: afficher tous les établissements par défaut
    # mais appliquer les filtres uniquement lorsque des filtres spécifiques sont utilisés
    # pour garder la compatibilité avec les tests existants

    # Vérifier si des filtres spécifiques sont activement utilisés
    filtres_actifs = False
    if (
        request.method == "POST"
        or form_recherche.validate_on_submit()
        or (request.method == "GET" and form_recherche.validate())
    ):
        # Extraire les paramètres de filtre
        filtres = extraire_parametres_filtre(form=form_recherche)

        # Vérifier si des filtres significatifs sont présents
        # (exclure les champs vides, les valeurs par défaut, et le champ ville)
        # Note: ville est exclu car nous voulons l'utiliser pour centrer la carte, pas pour filtrer
        filtres_significatifs = {
            k: v
            for k, v in filtres.items()
            if v and v != "tous" and k not in ["latitude", "longitude", "ville"]
        }

        if filtres_significatifs:
            filtres_actifs = True
            query = filtrer_etablissements(query, **filtres)

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
        # Extraire les paramètres de filtre en utilisant la fonction centralisée
        filtres = extraire_parametres_filtre_api(request)
        format = (
            request.args.get("format", "json")
            if request.method == "GET"
            else request.get_json().get("format", "json")
        )

        # Applique les filtres en utilisant la fonction centralisée
        query = Etablissement.query
        query = filtrer_etablissements(query, **filtres)

        # Filtrer pour ne retourner que les établissements qui ont des flans
        # sauf si des filtres spécifiques sur les flans sont appliqués
        has_flan_filters = any(
            filtres.get(key) and filtres.get(key) != "tous"
            for key in ["type_pate", "type_saveur", "type_texture", "prix"]
        )

        if not has_flan_filters:
            # Utiliser une sous-requête pour vérifier l'existence de flans
            query = query.filter(
                Etablissement.id_etab.in_(db.session.query(Flan.id_etab).distinct())
            )

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
            Evaluation.query.join(Utilisateur)
            .filter(Evaluation.statut == "EN_ATTENTE", Utilisateur.is_admin == False)
            .all()
        )
        pending_flans = (
            Flan.query.join(Utilisateur)
            .filter(Flan.statut == "EN_ATTENTE", Utilisateur.is_admin == False)
            .all()
        )
        pending_etablissements = (
            Etablissement.query.join(Utilisateur)
            .filter(Etablissement.statut == "EN_ATTENTE", Utilisateur.is_admin == False)
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
    # Utiliser joinedload pour charger les photos
    etablissement = (
        db.session.query(Etablissement)
        .options(joinedload(Etablissement.photos))
        .filter(Etablissement.id_etab == id_etab)
        .first()
    )
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

    # Si c'est une requête POST, recréer le formulaire avec les données POST
    if request.method == "POST":
        form_etab = EtabForm(prefix="edit-etab", formdata=request.form)
        
        if form_etab.validate_on_submit():
            # Vérifier la logique métier : label ne peut être True que si visite est True
            label_value = form_etab.label.data == "Oui"
            visite_value = form_etab.visite.data == "Oui"

            if label_value and not visite_value:
                flash(
                    "Un établissement ne peut être labellisé que s'il a été visité.",
                    "error",
                )
                return redirect(
                    url_for("main.afficher_etablissement_unique", id_etab=id_etab)
                )

            # Si la validation a réussi, procéder à la mise à jour
            try:
                etablissement.nom = form_etab.nom.data
                etablissement.description = form_etab.description.data
                etablissement.adresse = form_etab.adresse.data
                etablissement.ville = form_etab.ville.data
                etablissement.code_postal = form_etab.code_postal.data
                etablissement.latitude = form_etab.latitude.data
                etablissement.longitude = form_etab.longitude.data
                etablissement.type_etab = form_etab.type_etab.data

                if current_user.is_admin:
                    etablissement.label = label_value
                    etablissement.visite = visite_value

                    # Appeler la méthode de validation du modèle
                    etablissement.valider_label_visite()

                db.session.commit()
                flash("L'établissement a été mis à jour avec succès!", "success")
            except ValueError as e:
                db.session.rollback()
                flash(str(e), "error")

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
    # Utiliser joinedload pour charger les évaluations
    flan_unique = (
        db.session.query(Flan)
        .options(joinedload(Flan.evaluations))
        .filter(Flan.id_flan == id_flan)
        .first()
    )
    if flan_unique is None:
        from flask import abort

        abort(404)
    form_eval = EvalForm(prefix="flan-eval")
    form_flan = NewFlanForm(prefix="edit-flan", obj=flan_unique)
    delete_form = DeleteForm()
    validate_form = ValidateForm()

    user_evaluation = None
    if current_user.is_authenticated:
        user_evaluation = Evaluation.query.filter_by(
            id_flan=id_flan, id_user=current_user.id_user
        ).first()

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
        user_evaluation=user_evaluation,
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
        # Vérifier si l'utilisateur a déjà une évaluation pour ce flan
        if evaluation:
            # L'utilisateur a déjà une évaluation, ne pas en créer une nouvelle
            flash(
                "Vous avez déjà évalué ce flan. Vous ne pouvez pas créer une nouvelle évaluation.",
                "warning",
            )
        else:
            try:
                # Créer une nouvelle évaluation directement
                new_evaluation = Evaluation(
                    visuel=float(str(form.visuel.data).replace(",", ".")),
                    texture=float(str(form.texture.data).replace(",", ".")),
                    pate=float(str(form.pate.data).replace(",", ".")),
                    gout=float(str(form.gout.data).replace(",", ".")),
                    description=form.description.data,
                    id_flan=id_flan,
                    id_user=current_user.id_user,
                    statut="EN_ATTENTE" if not current_user.is_admin else "VALIDE"
                )
                
                # Calculer la moyenne
                values = [v for v in [new_evaluation.visuel, new_evaluation.texture, new_evaluation.pate, new_evaluation.gout] if v is not None]
                if values:
                    new_evaluation.moyenne = sum(values) / len(values)
                else:
                    new_evaluation.moyenne = 0
                    
                db.session.add(new_evaluation)
                db.session.commit()
                flash("Votre évaluation a été créée avec succès!", "success")
            except IntegrityError:
                db.session.rollback()
                flash(
                    "Vous avez déjà évalué ce flan. Vous ne pouvez pas créer une nouvelle évaluation.",
                    "warning",
                )
            except Exception as e:
                print("Error during form submission:", e)
                flash(
                    "Une erreur est survenue lors de la création de l'évaluation: "
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


@main_bp.route("/evaluation/<int:id_eval>", methods=["GET"])
def afficher_evaluation_unique(id_eval):
    evaluation = db.session.get(Evaluation, id_eval)
    if evaluation is None:
        from flask import abort

        abort(404)
    flan_unique = db.session.get(Flan, evaluation.id_flan)
    if flan_unique is None:
        from flask import abort

        abort(404)
    form = EvalForm(prefix="eval-detail", obj=evaluation)
    delete_form = DeleteForm()
    validate_form = ValidateForm()

    # Le formulaire est maintenant initialisé avec l'objet evaluation
    # Les données sont automatiquement pré-remplies grâce à obj=evaluation

    return render_template(
        "page_evaluation.html",
        evaluation=evaluation,
        form=form,
        current_user=current_user,
        delete_form=delete_form,  # <-- Passe delete_form au template
        validate_form=validate_form,
        current_page="page_evaluation",
    )





@main_bp.route("/modifier_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def modifier_evaluation(id_eval):
    evaluation = db.session.get(Evaluation, id_eval)
    if evaluation is None:
        from flask import abort

        abort(404)
    form = EvalForm(prefix="eval-detail")
    
    # Pré-remplir le formulaire avec les valeurs existantes
    if not form.is_submitted():
        # Convertir les valeurs en chaînes avec format uniforme (toujours .0 pour les entiers)
        def convert_note_to_string(value):
            if value is None:
                return None
            try:
                float_value = float(value)
                rounded = round(float_value, 1)
                # Toujours retourner avec une décimale pour uniformité
                return f"{rounded:.1f}"
            except (ValueError, TypeError):
                return None
        
        # Convertir les valeurs en chaînes qui correspondent exactement aux options
        form.visuel.data = convert_note_to_string(evaluation.visuel)
        form.texture.data = convert_note_to_string(evaluation.texture)
        form.pate.data = convert_note_to_string(evaluation.pate)
        form.gout.data = convert_note_to_string(evaluation.gout)
        form.description.data = evaluation.description
        
        # Logs pour déboguer
        print(f"DEBUG SERVER: Evaluation {id_eval} values:")
        print(f"DEBUG SERVER: visuel = {evaluation.visuel} (type: {type(evaluation.visuel)}) -> {form.visuel.data}")
        print(f"DEBUG SERVER: texture = {evaluation.texture} (type: {type(evaluation.texture)}) -> {form.texture.data}")
        print(f"DEBUG SERVER: pate = {evaluation.pate} (type: {type(evaluation.pate)}) -> {form.pate.data}")
        print(f"DEBUG SERVER: gout = {evaluation.gout} (type: {type(evaluation.gout)}) -> {form.gout.data}")
    
    if current_user.id_user != evaluation.id_user and not current_user.is_admin:
        flash("Vous n'avez pas le droit de modifier cette évaluation.", "danger")
        return redirect(url_for("main.afficher_evaluation_unique", id_eval=id_eval))
    if form.validate_on_submit():
        # Mettre à jour directement les champs comme dans modifier_flan
        evaluation.visuel = float(str(form.visuel.data).replace(",", "."))
        evaluation.texture = float(str(form.texture.data).replace(",", "."))
        evaluation.pate = float(str(form.pate.data).replace(",", "."))
        evaluation.gout = float(str(form.gout.data).replace(",", "."))
        evaluation.description = form.description.data
        
        # Recalculer la moyenne
        values = [v for v in [evaluation.visuel, evaluation.texture, evaluation.pate, evaluation.gout] if v is not None]
        if values:
            evaluation.moyenne = sum(values) / len(values)
        else:
            evaluation.moyenne = 0
            
        if current_user.is_admin:
            evaluation.statut = "VALIDE"
            
        db.session.commit()
        flash("L'évaluation a été mise à jour avec succès!", "success")
    else:
        flash(
            "Le formulaire n'a pas été validé. Veuillez vérifier les erreurs.", "danger"
        )
    return redirect(url_for("main.afficher_evaluation_unique", id_eval=id_eval))


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
