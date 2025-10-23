from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db, bcrypt
from app.forms import EvalForm, NewFlanForm, RechercheForm, UpdateProfileForm, EtabForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app.outils import afficher_etablissements

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from app.outils import afficher_etablissements
    form_edit = EtabForm(prefix='edit-etab')
    form_ajout = EtabForm(prefix='ajout-etab')
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'],
                           form_edit=form_edit,
                           form_ajout=form_ajout)

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    for eval in current_user.evaluations:
        print(
            f"Evaluation {eval.id_eval}: flan={eval.flan}, etablissement={eval.flan.etablissement if eval.flan else None}, nom={eval.flan.etablissement.nom if eval.flan and eval.flan.etablissement else None}")

    profile_form = UpdateProfileForm(prefix='profile')
    eval_form = EvalForm(prefix='dashboard-eval')
    pending_evaluations = []
    pending_flans = []
    pending_etablissements = []
    if current_user.is_admin:
        pending_evaluations = Evaluation.query.filter_by(statut='EN_ATTENTE').join(Utilisateur).filter(Utilisateur.is_admin == False).all()
        pending_flans = Flan.query.filter_by(statut='EN_ATTENTE').join(Utilisateur).filter(Utilisateur.is_admin == False).all()
        pending_etablissements = Etablissement.query.filter_by(statut='EN_ATTENTE').join(Utilisateur).filter(Utilisateur.is_admin == False).all()

    if request.method == 'POST' and profile_form.validate_on_submit():
        if profile_form.email.data and profile_form.email.data != current_user.email:
            existing_user = Utilisateur.query.filter(Utilisateur.email == profile_form.email.data).first()
            if existing_user and existing_user.id_user != current_user.id_user:
                flash('Cet email est déjà utilisé par un autre utilisateur.', 'danger')
                return redirect(url_for('main.dashboard'))

        current_user.pseudo = profile_form.pseudo.data
        if profile_form.email.data:
            current_user.email = profile_form.email.data
        if profile_form.new_password.data:
            current_user.password = bcrypt.generate_password_hash(profile_form.new_password.data).decode('utf-8')
        try:
            db.session.commit()
            flash('Votre profil a été mis à jour!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Une erreur est survenue lors de la mise à jour de votre profil.', 'danger')
        return redirect(url_for('main.dashboard'))

    elif request.method == 'GET':
        profile_form.pseudo.data = current_user.pseudo
        profile_form.email.data = current_user.email

    return render_template('dashboard.html',
                          title='Tableau de bord',
                          profile_form=profile_form,
                          eval_form=eval_form,
                          pending_evaluations=pending_evaluations,
                           pending_flans=pending_flans,
                           pending_etablissements=pending_etablissements)

@main_bp.route('/rechercher', methods=['GET', 'POST'])
def rechercher():
    form_recherche = RechercheForm(prefix='recherche')
    form_ajout = EtabForm(prefix='ajout-etab')
    form_edit = EtabForm(prefix='edit-etab')  # Formulaire générique pour l'édition
    query = Etablissement.query

    def apply_filters(query, params):
        search_term = params.get('nom')
        if search_term:
            query = query.filter(
                (Etablissement.nom.ilike(f'%{search_term}%')) |
                (Etablissement.ville.ilike(f'%{search_term}%'))
            )
        ville = params.get('ville')
        if ville:
            query = query.filter(Etablissement.ville.ilike(f'%{ville}%'))
        type_saveur = params.get('type_saveur')
        if type_saveur and type_saveur != 'tous':
            query = query.join(Flan).filter(Flan.type_saveur == type_saveur)
        type_pate = params.get('type_pate')
        if type_pate and type_pate != 'tous':
            query = query.join(Flan).filter(Flan.type_pate == type_pate)
        type_texture = params.get('type_texture')
        if type_texture and type_texture != 'tous':
            query = query.join(Flan).filter(Flan.type_texture == type_texture)
        prix = params.get('prix')
        if prix and prix != 'tous':
            if prix == '0':
                query = query.join(Flan).filter(Flan.prix < 2.5)
            elif prix == '2.5':
                query = query.join(Flan).filter(Flan.prix >= 2.5, Flan.prix < 5)
            elif prix == '5':
                query = query.join(Flan).filter(Flan.prix >= 5)
        if params.get('visite') == 'oui':
            query = query.filter(Etablissement.visite == 1)
        elif params.get('visite') == 'non':
            query = query.filter(Etablissement.visite == 0)
        if params.get('labellise') == 'oui':
            query = query.filter(Etablissement.label == 1)
        elif params.get('labellise') == 'non':
            query = query.filter(Etablissement.label == 0)
        return query

    if request.method == 'GET':
        has_search_params = any(request.args.get(k) for k in ['nom', 'ville', 'type_saveur', 'type_pate', 'type_texture', 'prix', 'visite', 'labellise'])
        if has_search_params:
            query = apply_filters(query, request.args)
            if query is None:
                flash("Erreur lors de l'application des filtres.", "error")
                return redirect(url_for('main.rechercher'))
        else:
            return render_template('rechercher.html', form_recherche=form_recherche, form_ajout=form_ajout, form_edit=form_edit)  # Passe un formulaire d'édition générique)
    elif form_recherche.validate_on_submit():
        query = apply_filters(query, {
            'nom': form_recherche.nom.data,
            'ville': form_recherche.ville.data,
            'type_saveur': form_recherche.type_saveur.data,
            'type_pate': form_recherche.type_pate.data,
            'type_texture': form_recherche.type_texture.data,
            'prix': form_recherche.prix.data,
            'visite': form_recherche.visite.data,
            'labellise': form_recherche.labellise.data
        })
        if query is None:
            flash("Erreur lors de l'application des filtres.", "error")
            return redirect(url_for('main.rechercher'))
    else:
        return render_template('rechercher.html', form_recherche=form_recherche, form_ajout=form_ajout, form_edit=form_edit)

    # Vérifie que query est bien une requête valide avant d'appeler .all()
    if query is None:
        flash("La requête est invalide.", "error")
        return redirect(url_for('main.rechercher'))

    resultats = query.all()
    if not resultats:
        flash("Aucun établissement trouvé avec ces critères.", "info")

    etablissements, etablissements_json = afficher_etablissements(resultats)
    session['resultats_recherche'] = etablissements_json
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'],
                           form_ajout=form_ajout, form_edit=form_edit)


@main_bp.route('/etablissement/<int:id_etab>', methods=['GET', 'POST'])
def afficher_etablissement_unique(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form_flan = NewFlanForm(prefix='ajout-flan')
    form_flan.id_etab.data = id_etab
    form_etab = EtabForm(prefix='edit-etab', obj=etablissement)

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
        flash('L\'établissement a été mis à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_etablissement_unique', id_etab=id_etab))

    return render_template('page_etablissement.html',
                          etablissement=etablissement,
                          form_flan=form_flan,
                          form_etab=form_etab,
                          current_user=current_user)

@main_bp.route('/flan/<int:id_flan>', methods=['GET', 'POST'])
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form_eval = EvalForm(prefix='flan-eval')
    form_flan = NewFlanForm(prefix='edit-flan', obj=flan_unique)

    # Traitement de la soumission du formulaire d'édition du flan
    if form_flan.validate_on_submit():
        flan_unique.nom = form_flan.nom.data
        flan_unique.description = form_flan.description.data
        flan_unique.prix = form_flan.prix.data
        flan_unique.type_pate = form_flan.type_pate.data
        flan_unique.type_saveur = form_flan.type_saveur.data
        flan_unique.type_texture = form_flan.type_texture.data
        db.session.commit()
        flash('Le flan a été mis à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

    # Création d'un dictionnaire de formulaires d'édition pour chaque évaluation
    eval_forms = {}
    for eval in flan_unique.evaluations:
        prefix = f'eval-edit-{eval.id_eval}'
        eval_forms[eval.id_eval] = EvalForm(prefix=prefix, obj=eval)

    return render_template('page_flan.html',
                          flan=flan_unique,
                          form_eval=form_eval,
                          form_flan=form_flan,
                          eval_forms=eval_forms)



@main_bp.route('/etablissement/<int:id_etab>/proposer_flan', methods=['GET', 'POST'])
@login_required
def proposer_flan(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form = NewFlanForm(prefix='ajout-flan')
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
            id_user=current_user.id_user
        )
        db.session.add(flan)
        db.session.commit()
        flash('Votre flan a été proposé avec succès !', 'success')
        return redirect(url_for('main.afficher_etablissement_unique', id_etab=id_etab))
    return render_template('page_etablissement.html', form=form, etablissement=etablissement)

@main_bp.route('/valider_flan/<int:id_flan>', methods=['POST'])
@login_required
def valider_flan(id_flan):
    if not current_user.is_admin:
        flash('Vous n\'avez pas le droit d\'accéder à cette page.', 'danger')
        return redirect(url_for('main.dashboard'))
    flan = Flan.query.get_or_404(id_flan)
    flan.statut = 'valide'
    try:
        db.session.commit()
        flash('Le flan a été validé avec succès!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Une erreur est survenue lors de la validation du flan.', 'danger')
    return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

@main_bp.route('/modifier_flan/<int:id_flan>', methods=['POST'])
@login_required
def modifier_flan(id_flan):
    flan = Flan.query.get_or_404(id_flan)
    form = NewFlanForm(prefix='edit-flan')
    if current_user.id_user != flan.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de modifier ce flan.', 'danger')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))
    if form.validate_on_submit():
        flan.nom = form.nom.data
        flan.type_saveur = form.type_saveur.data
        flan.type_texture = form.type_texture.data
        flan.type_pate = form.type_pate.data
        flan.description = form.description.data
        flan.prix = form.prix.data
        db.session.commit()
        flash('Le flan a été mis à jour avec succès!', 'success')
    else:
        flash('Le formulaire n\'a pas été validé. Veuillez vérifier les erreurs.', 'danger')
    return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

@main_bp.route('/supprimer_flan/<int:id_flan>', methods=['POST'])
@login_required
def supprimer_flan(id_flan):
    flan = Flan.query.get_or_404(id_flan)
    if current_user.id_user != flan.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de supprimer ce flan.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(flan)
    try:
        db.session.commit()
        flash('Le flan a été supprimé avec succès!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression du flan.', 'danger')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/flan/<int:id_flan>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_flan(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form = EvalForm(prefix='ajout-eval')

    if form.validate_on_submit():
        moyenne = (float(form.visuel.data) + float(form.texture.data) + float(form.pate.data) + float(
            form.gout.data)) / 4
        evaluation = Evaluation(
            visuel=form.visuel.data,
            texture=form.texture.data,
            pate=form.pate.data,
            gout=form.gout.data,
            description=form.description.data,
            id_flan=id_flan,
            id_user=current_user.id_user,
            moyenne=moyenne
        )
        db.session.add(evaluation)
        db.session.commit()
        flash('Votre évaluation a été proposée avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

    return render_template(
        'page_flan.html',
        flan=flan_unique,
        form=form
    )


@main_bp.route('/evaluation/<int:id_eval>', methods=['GET', 'POST'])
@login_required
def afficher_evaluation_unique(id_eval):
    evaluation = Evaluation.query.get_or_404(id_eval)
    flan_unique = Flan.query.get_or_404(evaluation.id_flan)

    # Formulaire pour modifier l'évaluation existante
    form_eval = EvalForm(prefix=f'eval-edit-{id_eval}', obj=evaluation)

    # Traitement de la soumission du formulaire d'édition de l'évaluation
    if form_eval.validate_on_submit():
        evaluation.visuel = form_eval.visuel.data
        evaluation.texture = form_eval.texture.data
        evaluation.pate = form_eval.pate.data
        evaluation.gout = form_eval.gout.data
        evaluation.description = form_eval.description.data

        # Recalculer la moyenne
        moyenne = (float(evaluation.visuel) + float(evaluation.texture) + float(evaluation.pate) + float(evaluation.gout)) / 4
        evaluation.moyenne = moyenne

        db.session.commit()
        flash('L\'évaluation a été mise à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_evaluation_unique', id_eval=id_eval))

    return render_template(
        'page_evaluation.html',
        evaluation=evaluation,
        flan=flan_unique,
        form=form_eval,
        current_user=current_user
    )


@main_bp.route('/flan/<int:id_flan>/proposer_evaluation', methods=['GET', 'POST'])
@login_required
def proposer_evaluation(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form = EvalForm(prefix='ajout-eval')

    if form.validate_on_submit():
        moyenne = (float(form.visuel.data) + float(form.texture.data) + float(form.pate.data) + float(form.gout.data)) / 4
        evaluation = Evaluation(
            visuel=form.visuel.data,
            texture=form.texture.data,
            pate=form.pate.data,
            gout=form.gout.data,
            description=form.description.data,
            id_flan=id_flan,
            id_user=current_user.id_user,
            moyenne=moyenne
        )
        db.session.add(evaluation)
        db.session.commit()
        flash('Votre évaluation a été proposée avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

    return render_template(
        'page_flan.html',
        flan=flan_unique,
        form=form
    )



@main_bp.route('/valider_evaluation/<int:id_eval>', methods=['POST'])
@login_required
def valider_evaluation(id_eval):
    if not current_user.is_admin:
        flash('Vous n\'avez pas le droit d\'accéder à cette page.', 'danger')
        return redirect(url_for('main.dashboard'))
    evaluation = Evaluation.query.get_or_404(id_eval)
    evaluation.statut = 'VALIDE'
    try:
        db.session.commit()
        flash('L\'évaluation a été validée avec succès!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Une erreur est survenue lors de la validation de l\'évaluation.', 'danger')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/supprimer_evaluation/<int:id_eval>', methods=['POST'])
@login_required
def supprimer_evaluation(id_eval):
    evaluation = Evaluation.query.get_or_404(id_eval)
    if current_user.id_user != evaluation.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de supprimer cette évaluation.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(evaluation)
    try:
        db.session.commit()
        flash('L\'évaluation a été supprimée avec succès!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression de l\'évaluation.', 'danger')
    return redirect(url_for('main.dashboard'))
