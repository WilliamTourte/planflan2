from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.forms import EvalForm, NewFlanForm, ChercheEtabForm, UpdateProfileForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app import db, bcrypt

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    from app.outils import afficher_etablissements
    # Redirection automatique vers la liste des établissements
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,  # Pour la grille
                           etablissements_json=etablissements_json,  # Pour la carte
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateProfileForm()
    pending_evaluations = []  # Initialisez avec une liste vide par défaut
    # L'administrateur peut voir les évaluations en attente
    if current_user.is_admin:
        pending_evaluations = Evaluation.query.filter_by(statut='EN_ATTENTE').all()

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


@main_bp.route('/modifier_evaluation/<int:id_eval>', methods=['POST'])
@login_required
def modifier_evaluation(id_eval):
    evaluation = Evaluation.query.get_or_404(id_eval)
    if current_user.id_user != evaluation.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de modifier cette évaluation.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Mise à jour des champs de l'évaluation avec les valeurs du formulaire
    evaluation.visuel = request.form.get('visuel', evaluation.visuel)
    evaluation.texture = request.form.get('texture', evaluation.texture)
    evaluation.pate = request.form.get('pate', evaluation.pate)
    evaluation.gout = request.form.get('gout', evaluation.gout)
    evaluation.description = request.form.get('description', evaluation.description)

    # Recalculer la moyenne
    moyenne = (
        float(evaluation.visuel) +
        float(evaluation.texture) +
        float(evaluation.pate) +
        float(evaluation.gout)
    ) / 4
    evaluation.moyenne = moyenne

    try:
        db.session.commit()
        flash('L\'évaluation a été modifiée avec succès!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Une erreur est survenue lors de la modification de l\'évaluation.', 'danger')

    # Redirige vers la route evaluer_flan avec l'ID du flan associé à cette évaluation
    return redirect(url_for('main.evaluer_flan', id_flan=evaluation.id_flan))


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

@main_bp.route('/rechercher', methods=['GET', 'POST'])
def rechercher():
    from app.outils import afficher_etablissements
    form = ChercheEtabForm()
    query = Etablissement.query

    def apply_filters(query, params):
        search_term = params.get('nom')  # Supposons que le terme de recherche est passé sous le paramètre 'nom'
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
            return render_template('rechercher.html', form=form)
    elif form.validate_on_submit():
        query = apply_filters(query, {
            'nom': form.nom.data,
            'ville': form.ville.data,
            'visite': form.visite.data,
            'labellise': form.labellise.data
        })
    else:
        return render_template('rechercher.html', form=form)

    resultats = query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    session['resultats_recherche'] = etablissements_json
    return render_template('liste_etablissements.html',
                           etablissements=etablissements,
                           etablissements_json=etablissements_json,
                           google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])



@main_bp.route('/etablissement/<int:id_etab>', methods=['GET', 'POST'])
def afficher_etablissement_unique(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form = NewFlanForm()  # Instancie un formulaire si on veut proposer un nouveau flan
    form.id_etab.data = id_etab  # Remplit le champ caché
    if form.validate_on_submit():  # Si le formulaire est soumis et valide

        pass
    # Passe toujours le formulaire au template, même en GET
    return render_template('page_etablissement.html', etablissement=etablissement, form=form, current_user=current_user)

@main_bp.route('/flan/<int:id_flan>')
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan) # Récupère le flan par son ID ou 404 si l'id n'existe pas
    evaluations = flan_unique.evaluations # Pour que les évaluations soient transmises

    return render_template('page_flan.html', flan=flan_unique, request=request) # request pour se souvenir du endpoint  # Passe le flan au template

@main_bp.route('/etablissement/<int:id_etab>/proposer_flan', methods=['GET', 'POST'])
@login_required
def proposer_flan(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form = NewFlanForm()
    # Pré-remplir le champ caché id_etab
    form.id_etab.data = id_etab
    if form.validate_on_submit():
        flan = Flan(
            nom=form.nom.data,
            description=form.description.data,
            prix=form.prix.data,
            id_etab=id_etab,
            id_user=current_user.id_user
        )
        db.session.add(flan)
        db.session.commit()
        flash('Votre flan a été proposé avec succès !', 'success')
        return redirect(url_for('main.afficher_etablissement_unique', id_etab=id_etab))
    return render_template('page_etablissement.html', form=form, etablissement=etablissement)




@main_bp.route('/flan/<int:id_flan>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_flan(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)
    form = EvalForm()
    # Vérifier si une évaluation existe déjà pour cet utilisateur et ce flan
    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=current_user.id_user).first()
    if form.validate_on_submit():
        moyenne = (
            float(form.visuel.data) +
            float(form.texture.data) +
            float(form.pate.data) +
            float(form.gout.data)
        ) / 4
        if evaluation:
            # Mettre à jour l'évaluation existante
            evaluation.visuel = form.visuel.data
            evaluation.texture = form.texture.data
            evaluation.pate = form.pate.data
            evaluation.gout = form.gout.data
            evaluation.description = form.description.data
            evaluation.moyenne = moyenne
        else:
            # Créer une nouvelle évaluation
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
            # Les évaluations de l'admin sont validées automatiquement
            if current_user.is_admin:
                evaluation.statut = 'VALIDE'

        db.session.add(evaluation)
        db.session.commit()
        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))
    # Si c'est une requête GET ou si le formulaire n'est pas valide, affichez le formulaire
    return render_template('evaluer_flan.html', form=form, flan=flan_unique)