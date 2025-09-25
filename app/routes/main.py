from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.forms import EvalForm, EtabForm
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

@main_bp.route('/etablissements')
def afficher_etablissements():
    etablissements = Etablissement.query.all() # Prend tous les établissements
    return render_template('liste_etablissements.html', etablissements=etablissements)

@main_bp.route('/etablissement/<int:id_etab>')   # Capture l'ID dans l'URL
def afficher_etablissement_unique(id_etab):
    etab_unique = Etablissement.query.get_or_404(id_etab)  # Récupère l'établissement par son ID ou 404
    return render_template('page_etablissement.html', etablissement=etab_unique)  # Passe l'établissement au template

@main_bp.route('/flan/<int:id_flan>')
def afficher_flan_unique(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan) # Récupère le flan par son ID ou 404 si l'id n'existe pas
    return render_template('flan.html', flan=flan_unique)  # Passe le flan au template

@main_bp.route('/flan/<int:id_flan>/evaluer', methods=['GET', 'POST'])
@login_required
def evaluer_flan(id_flan):
    flan_unique = Flan.query.get_or_404(id_flan)  # Récupère le flan par son ID ou 404 si l'id n'existe pas

    form=EvalForm()
    if form.validate_on_submit():  # Si le formulaire est soumis et valide
        evaluation=Evaluation(
            visuel = form.visuel.data,
            texture = form.texture.data,
            pate = form.pate.data,
            gout = form.gout.data,
        description = form.description.data,
        id_user=current_user.id # récupère l'id par Flask Login
        )
        db.session.add(evaluation)
        db.session.commit()

        return redirect(url_for('main.flan_detail', id_flan=id_flan))  # Redirige vers la page du flan
    # Affiche le formulaire (GET)
    return render_template('evaluer_flan.html', form=form, flan=flan)