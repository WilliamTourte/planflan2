

from flask import Blueprint, render_template, jsonify, request, flash, current_app

from app import db
from app.models import Etablissement

maps_bp = Blueprint('maps', __name__, template_folder='../templates')

@maps_bp.route('/carte')
def afficher_carte():
    return render_template('carte.html', google_maps_api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@maps_bp.route('/api/etablissements')
def get_etablissements():
    etablissements = Etablissement.query.all()
    return jsonify([{
        'nom': etablissement.nom,
        'latitude': float(etablissement.latitude),
        'longitude': float(etablissement.longitude),
    } for etablissement in etablissements])

@maps_bp.route('/api/ajouter_etablissement', methods=['POST'])
def ajouter_etablissement():
    data = request.json

    nouvel_etablissement = Etablissement(nom=data['nom'], latitude=data['latitude'], longitude=data['longitude'])
    db.session.add(nouvel_etablissement)
    db.session.commit()
    flash('Nouvel établissement ajouté', 'success')
