from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user, AnonymousUserMixin
from sqlalchemy.exc import IntegrityError
from app.forms import EvalForm, NewFlanForm, RechercheForm, UpdateProfileForm, EtabForm, DeleteForm, ValidateForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app import db, bcrypt

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from app.outils import afficher_etablissements
    form_recherche=RechercheForm()
 
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template('index.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'],

                           form_recherche=form_recherche)

def mise_a_jour_evaluation(form, id_flan, id_user, is_admin=False):
    print("Form data received:", form.data)
    visuel = float(str(form.visuel.data).replace(',', '.')) if form.visuel.data is not None else None
    texture = float(str(form.texture.data).replace(',', '.')) if form.texture.data is not None else None
    pate = float(str(form.pate.data).replace(',', '.')) if form.pate.data is not None else None
    gout = float(str(form.gout.data).replace(',', '.')) if form.gout.data is not None else None
    description = form.description.data if form.description.data is not None else ''

    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=id_user).first()
    if evaluation:
        # Toujours mettre à jour tous les champs, même s'ils n'ont pas changé
        evaluation.visuel = visuel
        evaluation.texture = texture
        evaluation.pate = pate
        evaluation.gout = gout
        evaluation.description = description
        moyenne = (
            float(evaluation.visuel or 0) +
            float(evaluation.texture or 0) +
            float(evaluation.pate or 0) +
            float(evaluation.gout or 0)
        ) / 4
        evaluation.moyenne = moyenne
    else:
        moyenne = (
            float(visuel or 0) +
            float(texture or 0) +
            float(pate or 0) +
            float(gout or 0)
        ) / 4
        evaluation = Evaluation(
            visuel=visuel,
            texture=texture,
            pate=pate,
            gout=gout,
            description=description,
            id_flan=id_flan,
            id_user=id_user,
            moyenne=moyenne
        )
    if is_admin:
        evaluation.statut = 'VALIDE'
    db.session.add(evaluation)
    db.session.commit()
    return evaluation



@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form_ajout = EtabForm()  # Instancie le formulaire
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
                          form_ajout=form_ajout,
                          profile_form=profile_form,
                          eval_form=eval_form,
                          pending_evaluations=pending_evaluations,
                           pending_flans=pending_flans,
                           pending_etablissements=pending_etablissements)

from flask import redirect, url_for, request
from app.outils import afficher_etablissements

@main_bp.route('/rechercher', methods=['GET', 'POST'])
def rechercher():
    form_recherche = RechercheForm(prefix='recherche')

    # Récupère tous les établissements par défaut
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)

    if form_recherche.validate_on_submit() or (request.method == 'GET' and any(request.args.get(k) for k in ['ville', 'type'])):
        # Récupère les paramètres de recherche
        ville = request.args.get('ville') or (form_recherche.ville.data if form_recherche.validate_on_submit() else None)
        type_flan = request.args.get('type') or (form_recherche.type.data if form_recherche.validate_on_submit() else None)

        # Applique les filtres
        query = Etablissement.query
        if ville:
            query = query.filter(Etablissement.ville.ilike(f'%{ville}%'))
        if type_flan:
            query = query.join(Flan).filter(Flan.type == type_flan)

        resultats = query.all()
        etablissements, etablissements_json = afficher_etablissements(resultats)

        # Redirige vers liste_etablissements avec les résultats
        return redirect(url_for('main.liste_etablissements', **request.args))

    return render_template(
        'rechercher.html',
        form_recherche=form_recherche,
        etablissements=etablissements,
        etablissements_json=etablissements_json  # Toujours défini
    )

@main_bp.route('/liste_etablissements', methods=['GET'])
def liste_etablissements():
    # Récupère les paramètres de recherche depuis l'URL
    ville = request.args.get('ville', '')
    type_flan = request.args.get('type', '')

    # Applique les filtres (identique à la route /rechercher)
    query = Etablissement.query
    if ville:
        query = query.filter(Etablissement.ville.ilike(f'%{ville}%'))
    if type_flan:
        query = query.join(Flan).filter(Flan.type == type_flan)

    resultats = query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)

    return render_template(
        'liste_etablissements.html',
        etablissements=etablissements,
        etablissements_json=etablissements_json,
        google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY']
    )


@main_bp.route('/etablissement/<int:id_etab>', methods=['GET', 'POST'])
def afficher_etablissement_unique(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form_etab = EtabForm(prefix='edit-etab', obj=etablissement)
    delete_form = DeleteForm()
    validate_form = ValidateForm()
    form_flan = NewFlanForm(prefix='ajout-flan')

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
                          current_user=current_user,
                           delete_form=delete_form,
                           validate_form=validate_form)

@main_bp.route('/flan/<int:id_flan>', methods=['GET', 'POST'])
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form_eval = EvalForm(prefix='flan-eval')
    form_flan = NewFlanForm(prefix='edit-flan', obj=flan_unique)
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
        flash('Le flan a été mis à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))



    return render_template('page_flan.html',
                          flan=flan_unique,

                           form_eval=form_eval,
                          form_flan=form_flan,

                            current_user=current_user,
                           delete_form=delete_form,
                           validate_form=validate_form
                           )

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
    form = EvalForm(prefix='flan-eval')
    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=current_user.id_user).first()
    if request.method == 'GET' and evaluation:
        form.visuel.data = str(evaluation.visuel)
        form.texture.data = str(evaluation.texture)
        form.pate.data = str(evaluation.pate)
        form.gout.data = str(evaluation.gout)
        form.description.data = evaluation.description
    if form.validate_on_submit():
        try:
            evaluation = mise_a_jour_evaluation(form, id_flan, current_user.id_user, current_user.is_admin)
            flash('Votre évaluation a été mise à jour avec succès!', 'success')
        except Exception as e:
            print("Error during form submission:", e)
            flash('Une erreur est survenue lors de la mise à jour de l\'évaluation: ' + str(e), 'danger')
    else:
        if request.method == 'POST':
            print("Form validation errors:", form.errors)
            flash('Le formulaire n\'a pas été validé correctement. Veuillez vérifier les erreurs.', 'danger')
    return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))


@main_bp.route('/evaluation/<int:id_eval>', methods=['GET', 'POST'])
@login_required
def afficher_evaluation_unique(id_eval):
    evaluation = Evaluation.query.get_or_404(id_eval)
    flan_unique = Flan.query.get_or_404(evaluation.id_flan)
    form = EvalForm(prefix='eval-detail')
    delete_form = DeleteForm()
    validate_form = ValidateForm()


    if request.method == 'GET':
        form.visuel.data = evaluation.visuel
        form.texture.data = evaluation.texture
        form.pate.data = evaluation.pate
        form.gout.data = evaluation.gout
        form.description.data = evaluation.description
    if form.validate_on_submit():
        evaluation = mise_a_jour_evaluation(form, flan_unique.id_flan, current_user.id_user, current_user.is_admin)
        flash('L\'évaluation a été mise à jour avec succès!', 'success')
        return redirect(url_for('main.afficher_evaluation_unique', id_eval=evaluation.id_eval))
    return render_template('page_evaluation.html',
                           evaluation=evaluation, form=form, current_user=current_user,
                           delete_form=delete_form,  # <-- Passe delete_form au template
                            validate_form=validate_form,
                           current_page='page_evaluation')

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
