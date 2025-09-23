from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Etablissement

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
    return render_template('etablissements.html', etablissements=etablissements)

def lister_etablissements():
    etablissements = Etablissement.query.all()
    for etablissement in etablissements:
        print(f"ID: {etablissement.id_etab}, Nom: {etablissement.nom}, Adresse: {etablissement.adresse}")
    return etablissements