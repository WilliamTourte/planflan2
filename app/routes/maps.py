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
from app.forms import EvalForm, NewFlanForm, ChercheEtabForm, UpdateProfileForm, EtabForm
from app.models import Etablissement, Flan, Evaluation, Utilisateur, TypeEtab
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

@maps_bp.route('/extraire_infos_adresse', methods=['POST'])
def extraire_infos_adresse():
    data = request.get_json()
    adresse = data.get('adresse', '')
    code_postal = extraire_code_postal(adresse)
    ville = extraire_ville(adresse)
    adresse_nettoyee = nettoyer_adresse(adresse)
    return jsonify({
        'code_postal': code_postal,
        'ville': ville,
        'adresse_nettoyee': adresse_nettoyee
    })
from flask import jsonify, request, url_for
from app.models import Etablissement

@maps_bp.route('/verifier_etablissement', methods=['POST'])
def verifier_etablissement():
    data = request.get_json()
    nom = data.get('nom')
    adresse = data.get('adresse')

    # Vérifier si l'établissement existe déjà dans la base de données
    etablissement = Etablissement.query.filter_by(nom=nom, adresse=adresse).first()
    if etablissement:
        return jsonify({
            'exists': True,
            'url': url_for('main.afficher_etablissement_unique', id_etab=etablissement.id_etab)
        })
    else:
        return jsonify({'exists': False})



# Route pour afficher le formulaire d'ajout d'établissement
@maps_bp.route('/ajouter_etablissement', methods=['GET', 'POST'])
def ajouter_etablissement():
    form = EtabForm()
    form.type_etab.choices = [(type_etab.name, type_etab.value) for type_etab in TypeEtab]

    if form.validate_on_submit():
        nom = form.nom.data
        adresse = form.adresse.data
        code_postal = form.code_postal.data
        ville = form.ville.data
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        type_etab = form.type_etab.data
        label = form.label.data == 'Oui'  # Convertir 'Oui'/'Non' en booléen
        visite = form.visite.data == 'Oui'  # Convertir 'Oui'/'Non' en booléen
        description = form.description.data

        # Enregistrez les détails dans la base de données
        new_etablissement = Etablissement(
            nom=nom,
            adresse=adresse,
            code_postal=code_postal,
            ville=ville,
            latitude=latitude,
            longitude=longitude,
            type_etab=TypeEtab[type_etab],  # Assurez-vous que type_etab est une valeur valide pour TypeEtab
            id_user=current_user.id_user,
            label=label,
            visite=visite,
            description=description
        )
        db.session.add(new_etablissement)
        db.session.commit()
        flash('Établissement ajouté avec succès !', 'success')
        return redirect(url_for('main.index'))  # Rediriger vers une page appropriée

    return render_template('ajouter_etablissement.html', form=form, google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])
