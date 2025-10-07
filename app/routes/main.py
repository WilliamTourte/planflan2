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
    pending_evaluations = None
    if current_user.is_admin:
        pending_evaluations = Evaluation.query.filter_by(statut='EN_ATTENTE').all()

    if request.method == 'POST' and form.validate_on_submit():
        # Vérifiez si l'email a été modifié
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
    query = Etablissement.query
    # Vérifier si c'est une requête GET avec des paramètres de recherche
    if request.method == 'GET':
        # Vérifier si au moins un paramètre a une valeur non vide
        has_search_params = any(request.args.get(k) for k in ['nom', 'visite', 'labellise'])
        if not has_search_params:
            return render_template('rechercher.html', form=form)
        if 'nom' in request.args and request.args['nom']:
            query = query.filter(Etablissement.nom.ilike(f'%{request.args["nom"]}%'))
        if 'visite' in request.args:
            visite = request.args.get('visite')
            if visite == 'oui':
                query = query.filter(Etablissement.visite == 1)
            elif visite == 'non':
                query = query.filter(Etablissement.visite == 0)
        if 'labellise' in request.args:
            labellise = request.args.get('labellise')
            if labellise == 'oui':
                query = query.filter(Etablissement.label == 1)
            elif labellise == 'non':
                query = query.filter(Etablissement.label == 0)
    # Vérifier si c'est une requête POST avec des données de formulaire
    elif form.validate_on_submit():
        if form.nom.data:
            query = query.filter(Etablissement.nom.ilike(f'%{form.nom.data}%'))
        if form.visite.data == 'oui':
            query = query.filter(Etablissement.visite == 1)
        elif form.visite.data == 'non':
            query = query.filter(Etablissement.visite == 0)
        if form.labellise.data == 'oui':
            query = query.filter(Etablissement.label == 1)
        elif form.labellise.data == 'non':
            query = query.filter(Etablissement.label == 0)
    else:
        # Si aucune recherche n'est effectuée, afficher le formulaire de recherche
        return render_template('rechercher.html', form=form)
    resultats = query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    # Stocker les résultats dans la session
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
        # Traiter les données ici
        pass

    # Passe toujours le formulaire au template, même en GET
    return render_template('page_etablissement.html', etablissement=etablissement, form=form)

@main_bp.route('/flan/<int:id_flan>')
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan) # Récupère le flan par son ID ou 404 si l'id n'existe pas
    evaluations = flan_unique.evaluations # Pour que les évaluations soient transmises
    for eval in evaluations:
        print(f"ID: {eval.id_eval}, Statut: {eval.statut}")
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

        )
        db.session.add(flan)
        db.session.commit()
        flash('Votre flan a été proposé avec succès !', 'success')
        return redirect(url_for('main.afficher_etablissement_unique', id_etab=id_etab))

    return render_template('page_etablissement.html', form=form, etablissement=etablissement)


@main_bp.route('/flan/<int:id_flan>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_flan(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)  # Récupère le flan par son ID ou 404 si l'id n'existe pas

    form=EvalForm()
    if form.validate_on_submit():  # Si le formulaire est soumis et valide
        # Calcul de la moyenne
        moyenne = (
            float(form.visuel.data) +
            float(form.texture.data) +
            float(form.pate.data) +
            float(form.gout.data)
        ) / 4
        evaluation=Evaluation(
            visuel = form.visuel.data,
            texture = form.texture.data,
            pate = form.pate.data,
            gout = form.gout.data,
            description = form.description.data,
            id_flan=id_flan,
            id_user=current_user.id_user, # récupère l'id par Flask Login (current_user)
            moyenne=moyenne
        )
        db.session.add(evaluation)
        db.session.commit()

        return redirect(url_for('main.afficher_flan_unique', id_flan=id_flan))  # Redirige vers la page du flan
    # Affiche le formulaire (GET)
    return render_template('evaluer_flan.html', form=form, flan=flan_unique)