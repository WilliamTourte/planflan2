from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config
from app.outils import enlever_accents
import re

from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.forms import EvalForm, NewFlanForm, ChercheEtabForm, UpdateProfileForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur
from app import db, bcrypt

maps_bp = Blueprint('maps', __name__)


def extraire_code_postal(adresse):
    match = re.search(r'(\d{5})', adresse)
    return match.group(1) if match else None

def extraire_ville(adresse):
    match = re.search(r'\d{5}\s+([^,]+)', adresse)
    return match.group(1).strip() if match else None

def nettoyer_adresse(adresse):
    return adresse.split(',')[0].strip()

# Route pour afficher le formulaire d'ajout d'établissement
@maps_bp.route('/ajouter_etablissement', methods=['GET'])
def afficher_ajouter_etablissement():
    return render_template('ajouter_etablissement.html', google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])


# Ajouter la route pour ajouter un établissement
@maps_bp.route('/ajouter_etablissement', methods=['POST'])
def ajouter_etablissement():
    data = request.get_json()
    nom = data.get('nom')
    adresse = data.get('adresse')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Extraire le code postal et la ville de l'adresse
    code_postal = extraire_code_postal(adresse)
    ville = extraire_ville(adresse)
    adresse_nettoyee = nettoyer_adresse(adresse)

    # Enregistrez les détails dans la base de données
    from app.models import Etablissement, TypeEtab
    new_etablissement = Etablissement(
        nom=nom,
        adresse=adresse_nettoyee,
        code_postal=code_postal,
        ville=ville,
        latitude=latitude,
        longitude=longitude,
        type_etab=TypeEtab.BOULANGERIE,  # Par défaut, vous pouvez changer cela si nécessaire,
        id_user=current_user.id_user
    )
    db.session.add(new_etablissement)
    db.session.commit()


    return jsonify({"status": "success", "message": "Établissement ajouté avec succès"})
