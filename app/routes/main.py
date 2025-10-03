from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from app.forms import EvalForm, NewFlanForm, ChercheEtabForm
from app.models import Etablissement, Flan, Evaluation
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Redirection automatique vers la liste des établissements
    return redirect(url_for('main.afficher_etablissements'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/rechercher',  methods=['GET', 'POST'])
def rechercher():
    form = ChercheEtabForm()
    if form.validate_on_submit():
        pass
    return render_template('rechercher.html', form=form)


@main_bp.route('/etablissements')
def afficher_etablissements():
    etablissements = Etablissement.query.all()
    etablissements_json = [{
        'id_etab': etab.id_etab,
        'nom': etab.nom,
        'adresse': etab.adresse,
        'ville': etab.ville,
        'code_postal': etab.code_postal,
        'latitude': float(etab.latitude),
        'longitude': float(etab.longitude),
        'url': url_for('main.afficher_etablissement_unique', id_etab=etab.id_etab)
    } for etab in etablissements]

    return render_template('liste_etablissements.html',
                           etablissements=etablissements,  # Pour la grille
                           etablissements_json=etablissements_json,  # Pour la carte
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