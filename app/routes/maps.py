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

from flask import request, current_app, flash, redirect, url_for, render_template
from werkzeug.datastructures import MultiDict
from app.outils import afficher_etablissements

from flask import request, current_app, flash, redirect, url_for, render_template
from werkzeug.datastructures import MultiDict
from app.outils import afficher_etablissements

@maps_bp.route('/ajouter_etablissement', methods=['GET', 'POST'])
def ajouter_etablissement():
    form_ajout = EtabForm(prefix='ajout-etab')
    if request.method == 'POST':
        print("\n" + "="*80)
        print("NOUVELLE SOUMISSION POST")
        print("="*80)

        # 1. Afficher toutes les données brutes reçues
        print("\n1. DONNÉES BRUTES REÇUES:")
        form_data_raw = dict(request.form)
        for key, value in form_data_raw.items():
            print(f"   {key}: {value}")

        # 2. Créer une nouvelle instance de formulaire DIRECTEMENT avec les données brutes (sans renommage)
        form_ajout = EtabForm(prefix='ajout-etab', formdata=MultiDict(request.form))

        # 3. Vérifier la validation
        print("\n7. RÉSULTAT DE LA VALIDATION:")
        if form_ajout.validate():
            print("   ✅ FORMULAIRE VALIDE !")
            # 8. Afficher les données validées
            print("\n8. DONNÉES VALIDÉES:")
            for field_name, field in form_ajout._fields.items():
                print(f"   {field_name}: {getattr(form_ajout, field_name).data}")
            # Créer et sauvegarder le nouvel établissement
            nouvel_etablissement = Etablissement(
                nom=form_ajout.nom.data,
                adresse=form_ajout.adresse.data,
                code_postal=form_ajout.code_postal.data,
                ville=form_ajout.ville.data,
                latitude=form_ajout.latitude.data,
                longitude=form_ajout.longitude.data,
                type_etab=form_ajout.type_etab.data,
                description=form_ajout.description.data,
                id_user=current_user.id_user
            )
            # Ajouter les champs admin si présents dans le formulaire
            if hasattr(form_ajout, 'label') and form_ajout.label.data:
                nouvel_etablissement.label = (form_ajout.label.data == 'Oui')
                print(f"   Label: {nouvel_etablissement.label}")
            if hasattr(form_ajout, 'visite') and form_ajout.visite.data:
                nouvel_etablissement.visite = (form_ajout.visite.data == 'Oui')
                print(f"   Visite: {nouvel_etablissement.visite}")
            db.session.add(nouvel_etablissement)
            db.session.commit()
            flash("Établissement ajouté avec succès !", "success")
            return redirect(url_for('main.index'))
        else:
            print("   ❌ FORMULAIRE INVALIDE !")
            # 9. Afficher les erreurs de validation
            print("\n9. ERREURS DE VALIDATION:")
            for field_name, errors in form_ajout.errors.items():
                print(f"   {field_name}: {errors}")
            # 10. Vérifier les données du formulaire après validation échouée
            print("\n10. DONNÉES DU FORMULAIRE APRES ÉCHEC:")
            for field_name, field in form_ajout._fields.items():
                print(f"   {field_name}: {getattr(form_ajout, field_name).data}")
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
    # Pour une requête GET
    print("\nREQUÊTE GET - Affichage du formulaire")
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
