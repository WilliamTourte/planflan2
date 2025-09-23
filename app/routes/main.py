from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Etablissement, Flan

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/etablissements')
def afficher_etablissements():
    etablissements = lister_etablissements()
    return render_template('liste_etablissements.html', etablissements=etablissements)

def lister_etablissements():
    etablissements = Etablissement.query.all()
    return etablissements

@main_bp.route('/etablissement/<int:id_etab>')   # Capture l'ID dans l'URL
def afficher_etablissement_unique(id_etab):
    etab_unique = Etablissement.query.get(id_etab)  # Récupère l'établissement par son ID
    if etab_unique is None:
        abort(404)  # Retourne une erreur 404 si l'établissement n'existe pas
    return render_template('page_etablissement.html', etablissement=etab_unique)  # Passe l'établissement au template

@main_bp.route('/flan/<int:id_flan>')
def afficher_flan_unique(id_flan):
    flan = Flan.query.get_or_404(id_flan)
    return render_template('flan.html', flan=flan)

