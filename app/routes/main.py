from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.forms import EvalForm, NewFlanForm, ChercheEtabForm, UpdateProfileForm, EtabForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app import db, bcrypt

main_bp = Blueprint('main', __name__)

def mise_a_jour_evaluation(form, id_flan, id_user, is_admin=False):
    print("Form data:", form.data)  # Ajoutez cette ligne pour voir les données du formulaire
    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=id_user).first()
    moyenne = (
        float(form.visuel.data) +
        float(form.texture.data) +
        float(form.pate.data) +
        float(form.gout.data)
    ) / 4
    print("Moyenne calculée:", moyenne)  # Ajoutez cette ligne pour voir la moyenne calculée
    if evaluation:
        # Mettre à jour l'évaluation existante
        evaluation.visuel = form.visuel.data
        evaluation.texture = form.texture.data
        evaluation.pate = form.pate.data
        evaluation.gout = form.gout.data
        evaluation.description = form.description.data
        evaluation.moyenne = moyenne
        print("Évaluation existante mise à jour:", evaluation)  # Ajoutez cette ligne pour voir l'évaluation mise à jour
    else:
        # Créer une nouvelle évaluation
        evaluation = Evaluation(
            visuel=form.visuel.data,
            texture=form.texture.data,
            pate=form.pate.data,
            gout=form.gout.data,
            description=form.description.data,
            id_flan=id_flan,
            id_user=id_user,
            moyenne=moyenne
        )
        print("Nouvelle évaluation créée:", evaluation)  # Ajoutez cette ligne pour voir la nouvelle évaluation
    if is_admin:
        evaluation.statut = 'VALIDE'
    db.session.add(evaluation)
    db.session.commit()
    print("Évaluation sauvegardée dans la base de données")  # Ajoutez cette ligne pour confirmer la sauvegarde
    return evaluation


@main_bp.route('/')
def index():
    from app.outils import afficher_etablissements
    # Redirection automatique vers la liste des établissements
    form2 = EtabForm()
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'],
                           form2=form2)

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateProfileForm()
    pending_evaluations = []  # Initialisez avec une liste vide par défaut
    # L'administrateur peut voir les évaluations en attente des autres utilisateurs non administrateurs
    if current_user.is_admin:
        pending_evaluations = Evaluation.query.filter_by(statut='EN_ATTENTE').join(Utilisateur).filter(Utilisateur.is_admin == False).all()
    # Si demande de modification du profil
    if request.method == 'POST' and form.validate_on_submit():
        #  Email modifié ?
        if form.email.data and form.email.data != current_user.email:
            existing_user = Utilisateur.query.filter(Utilisateur.email == form.email.data).first()
            if existing_user and existing_user.id_user != current_user.id_user:
                flash('Cet email est déjà utilisé par un autre utilisateur.', 'danger')
                return redirect(url_for('main.dashboard'))
        current_user.pseudo = form.pseudo.data
        if form.email.data:  # Mettre à jour l'email uniquement s'il a été soumis
            current_user.email = form.email.data
        if form.new_password.data:
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        try:
            db.session.commit()
            flash('Votre profil a été mis à jour!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Une erreur est survenue lors de la mise à jour de votre profil.', 'danger')
        return redirect(url_for('main.dashboard'))
    elif request.method == 'GET':
        form.pseudo.data = current_user.pseudo
        form.email.data = current_user.email
    return render_template('dashboard.html', title='Tableau de bord', form=form, pending_evaluations=pending_evaluations)

@main_bp.route('/rechercher', methods=['GET', 'POST'])
def rechercher():
    from app.outils import afficher_etablissements
    form = ChercheEtabForm()
    form2 = EtabForm()
    query = Etablissement.query
    def apply_filters(query, params):
        search_term = params.get('nom')
        if search_term:
            query = query.filter(
                (Etablissement.nom.ilike(f'%{search_term}%')) |
                (Etablissement.ville.ilike(f'%{search_term}%'))
            )
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
        has_search_params = any(request.args.get(k) for k in ['nom', 'visite', 'labellise'])
        if has_search_params:
            query = apply_filters(query, request.args)
        else:
            return render_template('rechercher.html', form=form, form2=form2)
    elif form.validate_on_submit():
        query = apply_filters(query, {
            'nom': form.nom.data,
            'ville': form.ville.data,
            'visite': form.visite.data,
            'labellise': form.labellise.data
        })
    else:
        return render_template('rechercher.html', form=form, form2=form2)
    resultats = query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    session['resultats_recherche'] = etablissements_json
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'],
                           form2=form2)

### ROUTES D'AFFICHAGE POUR PAGES (ETABLISSEMENT, FLAN)###
@main_bp.route('/etablissement/<int:id_etab>', methods=['GET', 'POST'])
def afficher_etablissement_unique(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form_flan = NewFlanForm()  # Formulaire pour proposer un nouveau flan
    form_flan.id_etab.data = id_etab
    form_etab = EtabForm(obj=etablissement)  # Formulaire pour modifier l'établissement

    if form_flan.validate_on_submit():  # Si le formulaire pour proposer un flan est soumis
        flan = Flan(
            nom=form_flan.nom.data,
            description=form_flan.description.data,
            prix=form_flan.prix.data,
            type_pate=form_flan.type_pate.data,
            type_saveur=form_flan.type_saveur.data,
            type_texture=form_flan.type_texture.data,
            id_etab=id_etab,
            id_user=current_user.id_user
        )
        db.session.add(flan)
        db.session.commit()
        flash('Votre flan a été proposé avec succès !', 'success')
        return redirect(url_for('main.afficher_etablissement_unique', id_etab=id_etab))

    if form_etab.validate_on_submit():  # Si le formulaire pour modifier l'établissement est soumis
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

    return render_template('page_etablissement.html', etablissement=etablissement, form_flan=form_flan, form_etab=form_etab, current_user=current_user)

@main_bp.route('/flan/<int:id_flan>', methods=['GET', 'POST'])
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form_eval = EvalForm()  # Formulaire pour évaluer le flan
    form_flan = NewFlanForm(obj=flan_unique)  # Formulaire pour modifier le flan

    if form_eval.validate_on_submit():  # Si le formulaire pour évaluer le flan est soumis
        evaluation = mise_a_jour_evaluation(form_eval, id_flan, current_user.id_user, current_user.is_admin)
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

    if form_flan.validate_on_submit():  # Si le formulaire pour modifier le flan est soumis
        flan_unique.nom = form_flan.nom.data
        flan_unique.description = form_flan.description.data
        flan_unique.prix = form_flan.prix.data
        flan_unique.type_pate = form_flan.type_pate.data
        flan_unique.type_saveur = form_flan.type_saveur.data
        flan_unique.type_texture = form_flan.type_texture.data
        db.session.commit()
        flash('Le flan a été mis à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))

    return render_template('page_flan.html', flan=flan_unique, form_eval=form_eval, form_flan=form_flan, request=request)

### AUTOUR DU FLAN ###
@main_bp.route('/etablissement/<int:id_etab>/proposer_flan', methods=['GET', 'POST'])
@login_required
def proposer_flan(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form = NewFlanForm()
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
    form = NewFlanForm()
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

### EVALUATION ###
@main_bp.route('/flan/<int:id_flan>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_flan(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form = EvalForm()
    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=current_user.id_user).first()
    if request.method == 'GET' and evaluation:
        form.visuel.data = evaluation.visuel
        form.texture.data = evaluation.texture
        form.pate.data = evaluation.pate
        form.gout.data = evaluation.gout
        form.description.data = evaluation.description
    if form.validate_on_submit():
        evaluation = mise_a_jour_evaluation(form, id_flan, current_user.id_user, current_user.is_admin)
        flash('Votre évaluation a été mise à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))
    return render_template('page_flan.html', id_flan=id_flan, form=form, flan=flan_unique, evaluation=evaluation)


@main_bp.route('/evaluation/<int:id_eval>', methods=['GET', 'POST'])
@login_required
def afficher_evaluation_unique(id_eval):
    evaluation = Evaluation.query.get_or_404(id_eval)
    flan_unique = Flan.query.get_or_404(evaluation.id_flan)
    form = EvalForm()
    if request.method == 'GET':
        form.visuel.data = evaluation.visuel
        form.texture.data = evaluation.texture
        form.pate.data = evaluation.pate
        form.gout.data = evaluation.gout
        form.description.data = evaluation.description
    if form.validate_on_submit():
        print("Form data:", form.data)
        evaluation = mise_a_jour_evaluation(form, flan_unique.id_flan, current_user.id_user, current_user.is_admin)
        flash('L\'évaluation a été mise à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_evaluation_unique', id_eval=evaluation.id_eval))
    return render_template('page_evaluation.html', evaluation=evaluation, form=form, current_user=current_user)

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
