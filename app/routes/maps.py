

from flask import Blueprint, render_template, jsonify, request, flash, current_app, url_for

from app import db
from app.models import Etablissement

maps_bp = Blueprint('maps', __name__, template_folder='../templates')





@maps_bp.route('/api/etablissements')
def get_etablissements():
    etablissements = Etablissement.query.all()
    return jsonify([{
        'id': etablissement.id_etab,
        'nom': etablissement.nom,
        'adresse': etablissement.adresse,
        'ville': etablissement.ville,
        'postal_code': etablissement.code_postal,
        'latitude': float(etablissement.latitude),
        'longitude': float(etablissement.longitude),
        'url': url_for('main.afficher_etablissement_unique', id_etab=etablissement.id_etab)  #

    } for etablissement in etablissements])

@maps_bp.route('/api/ajouter_etablissement', methods=['POST'])
def ajouter_etablissement():
    data = request.json

    nouvel_etablissement = Etablissement(nom=data['nom'], latitude=data['latitude'], longitude=data['longitude'])
    db.session.add(nouvel_etablissement)
    db.session.commit()
    flash('Nouvel établissement ajouté', 'success')