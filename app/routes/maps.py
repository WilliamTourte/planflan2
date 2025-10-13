from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config
from app.outils import enlever_accents, afficher_etablissements
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




@maps_bp.route('/verifier_etablissement', methods=['POST'])
def verifier_etablissement():
    data = request.get_json()
    nom = data.get('nom')

    # Vérifier si l'établissement existe déjà dans la base de données
    etablissement = Etablissement.query.filter_by(nom=nom).first()
    if etablissement:
        print(f"Établissement trouvé : {etablissement.nom}, {etablissement.adresse}")
        return jsonify({
            'exists': True,
            'url': url_for('main.afficher_etablissement_unique', id_etab=etablissement.id_etab)
        })
    else:
        print("Aucun établissement trouvé avec ces critères.")
        return jsonify({'exists': False})



@login_required
@maps_bp.route('/ajouter_etablissement', methods=['GET', 'POST'])
def ajouter_etablissement():
    form = EtabForm()
    form.type_etab.choices = [(type_etab.name, type_etab.value) for type_etab in TypeEtab]
    etablissements = Etablissement.query.all()  # Récupérer tous les établissements
    etablissements, etablissements_json = afficher_etablissements(etablissements)  # Déballer le tuple
    if request.method == 'POST':
        nom = form.nom.data
        # Vérifier si l'établissement existe déjà dans la base de données
        etablissement_existe = Etablissement.query.filter_by(nom=nom).first()
        if etablissement_existe:
            flash('Un établissement avec ce nom existe déjà.', 'error')
            return render_template('liste_etablissements.html', form=form, etablissements_json=etablissements_json, google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])
        if form.validate_on_submit():
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
    return render_template('liste_etablissements.html', form2=form, etablissements_json=etablissements_json, google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@maps_bp.route('/modifier_etablissement/<int:id_etab>', methods=['GET', 'POST'])
@login_required
def modifier_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)
    form = EtabForm()
    form.type_etab.choices = [(type_etab.name, type_etab.value) for type_etab in TypeEtab]

    # Vérifier si l'utilisateur est l'auteur de l'établissement ou un admin
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de modifier cet établissement.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'GET':
        # Pré-remplir le formulaire avec les données de l'établissement
        form.nom.data = etablissement.nom
        form.adresse.data = etablissement.adresse
        form.code_postal.data = etablissement.code_postal
        form.ville.data = etablissement.ville
        form.latitude.data = etablissement.latitude
        form.longitude.data = etablissement.longitude
        form.type_etab.data = etablissement.type_etab.name  # Supposons que type_etab est un Enum
        form.label.data = 'Oui' if etablissement.label else 'Non'
        form.visite.data = 'Oui' if etablissement.visite else 'Non'
        form.description.data = etablissement.description

    elif request.method == 'POST':
        if form.validate_on_submit():
            # Mettre à jour les données de l'établissement
            etablissement.nom = form.nom.data
            etablissement.adresse = form.adresse.data
            etablissement.code_postal = form.code_postal.data
            etablissement.ville = form.ville.data
            etablissement.latitude = request.form.get('latitude')
            etablissement.longitude = request.form.get('longitude')
            etablissement.type_etab = TypeEtab[form.type_etab.data]
            etablissement.label = form.label.data == 'Oui'
            etablissement.visite = form.visite.data == 'Oui'
            etablissement.description = form.description.data

            db.session.commit()
            flash('Établissement mis à jour avec succès !', 'success')
            return redirect(url_for('main.index'))

    etablissements = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(etablissements)
    return render_template('liste_etablissements.html', form2=form, etablissements_json=etablissements_json, google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@maps_bp.route('/valider_etablissement/<int:id_etab>', methods=['POST'])
@login_required
def valider_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Vérifier si l'utilisateur est un admin
    if not current_user.is_admin:
        flash('Vous n\'avez pas le droit de valider cet établissement.', 'error')
        return redirect(url_for('main.index'))

    # Mettre à jour le statut de l'établissement
    etablissement.statut = 'valide'
    db.session.commit()
    flash('Établissement validé avec succès !', 'success')
    return redirect(url_for('main.index'))

@maps_bp.route('/supprimer_etablissement/<int:id_etab>', methods=['POST'])
@login_required
def supprimer_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Vérifier si l'utilisateur est l'auteur de l'établissement ou un admin
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de supprimer cet établissement.', 'error')
        return redirect(url_for('main.index'))

    # Supprimer l'établissement de la base de données
    db.session.delete(etablissement)
    db.session.commit()
    flash('Établissement supprimé avec succès !', 'success')
    return redirect(url_for('main.index'))
