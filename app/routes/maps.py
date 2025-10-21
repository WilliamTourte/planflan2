from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.datastructures import MultiDict

from app.config import Config
from app.outils import enlever_accents, afficher_etablissements
import re

from flask import Blueprint, session, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.forms import EvalForm, NewFlanForm, RechercheForm, UpdateProfileForm, EtabForm
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


@maps_bp.route('/ajouter_etablissement', methods=['GET', 'POST'])
def ajouter_etablissement():
    form_ajout = EtabForm(prefix='ajout-etab')
    if request.method == 'POST':
        form_ajout = EtabForm(prefix='ajout-etab', formdata=MultiDict(request.form))
        if form_ajout.validate():
            nouvel_etablissement = Etablissement(
                nom=form_ajout.nom.data,
                adresse=form_ajout.adresse.data,
                code_postal=form_ajout.code_postal.data,
                ville=form_ajout.ville.data,
                latitude=form_ajout.latitude.data,
                longitude=form_ajout.longitude.data,
                type_etab=form_ajout.type_etab.data,
                description=form_ajout.description.data,
                id_user=current_user.id_user,
                label=form_ajout.label.data,  # Directement un booléen
                visite=form_ajout.visite.data  # Directement un booléen
            )
            db.session.add(nouvel_etablissement)
            db.session.commit()
            flash("Établissement ajouté avec succès !", "success")
            return redirect(url_for('main.index'))
        else:
            print("\n9. ERREURS DE VALIDATION:")
            for field_name, errors in form_ajout.errors.items():
                print(f"   {field_name}: {errors}")
    # Pour une requête GET
    resultats = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(resultats)
    return render_template(
        'liste_etablissements.html',
        etablissements=etablissements,
        etablissements_json=etablissements_json,
        form_ajout=form_ajout,
        form_edit=EtabForm(prefix='edit-etab'),
        google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY']
    )


@maps_bp.route('/modifier_etablissement/<int:id_etab>', methods=['GET', 'POST'])
@login_required
def modifier_etablissement(id_etab):
    etablissement = Etablissement.query.get_or_404(id_etab)

    # Instanciation des formulaires avec leurs préfixes respectifs
    form_edit = EtabForm(prefix='edit-etab')
    form_ajout = EtabForm(prefix='ajout-etab')

    # Définition des choix pour les deux formulaires
    form_edit.type_etab.choices = [(type_etab.name, type_etab.value) for type_etab in TypeEtab]
    form_ajout.type_etab.choices = [(type_etab.name, type_etab.value) for type_etab in TypeEtab]

    # Vérification des droits
    if current_user.id_user != etablissement.id_user and not current_user.is_admin:
        flash('Vous n\'avez pas le droit de modifier cet établissement.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'GET':
        # Pré-remplissage du formulaire d'édition
        form_edit.nom.data = etablissement.nom
        form_edit.adresse.data = etablissement.adresse
        form_edit.code_postal.data = etablissement.code_postal
        form_edit.ville.data = etablissement.ville
        form_edit.latitude.data = etablissement.latitude
        form_edit.longitude.data = etablissement.longitude
        form_edit.type_etab.data = etablissement.type_etab.name
        form_edit.label.data = 'Oui' if etablissement.label else 'Non'
        form_edit.visite.data = 'Oui' if etablissement.visite else 'Non'
        form_edit.description.data = etablissement.description

    elif request.method == 'POST':
        # Recréation du formulaire d'édition avec les données POST
        form_edit = EtabForm(prefix='edit-etab', formdata=request.form)
        if form_edit.validate_on_submit():
            # Mise à jour des données de l'établissement
            etablissement.nom = form_edit.nom.data
            etablissement.adresse = form_edit.adresse.data
            etablissement.code_postal = form_edit.code_postal.data
            etablissement.ville = form_edit.ville.data
            etablissement.latitude = form_edit.latitude.data  # Utilisation de form_edit au lieu de request.form
            etablissement.longitude = form_edit.longitude.data  # Utilisation de form_edit au lieu de request.form
            etablissement.type_etab = TypeEtab[form_edit.type_etab.data]
            etablissement.label = form_edit.label.data == 'Oui'
            etablissement.visite = form_edit.visite.data == 'Oui'
            etablissement.description = form_edit.description.data
            db.session.commit()
            flash('Établissement mis à jour avec succès !', 'success')
            return redirect(url_for('main.index'))

    # Récupération de tous les établissements pour l'affichage
    etablissements = Etablissement.query.all()
    etablissements, etablissements_json = afficher_etablissements(etablissements)

    # Rendement du template avec tous les éléments nécessaires
    return render_template(
        'liste_etablissements.html',
        form_edit=form_edit,          # Formulaire d'édition pré-rempli
        form_ajout=form_ajout,        # Formulaire d'ajout vide
        etablissements_json=etablissements_json,
        google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY']
    )



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
