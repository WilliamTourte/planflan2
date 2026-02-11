"""API Etablissements - Endpoints pour la recherche d'établissements."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Etablissement
from app.extensions import db

# Créer un blueprint pour les endpoints API des établissements
etablissements_api_bp = Blueprint("etablissements_api", __name__, url_prefix="/api/etablissements")


@etablissements_api_bp.route("/", methods=["GET"])
def search_etablissements():
    """Recherche des établissements par ville et/ou nom.
    
    Args:
        ville (str): Nom de la ville pour filtrer les établissements
        q (str): Terme de recherche pour le nom de l'établissement
        
    Returns:
        JSON: Liste des établissements correspondant aux critères
    """
    ville = request.args.get("ville", "")
    query_search = request.args.get("q", "")
    
    # Construire la requête de base
    etablissements_query = Etablissement.query
    
    # Filtrer par ville si spécifiée
    if ville:
        etablissements_query = etablissements_query.filter(
            Etablissement.ville.ilike(f"%{ville}%")
        )
    
    # Filtrer par nom si spécifié
    if query_search:
        etablissements_query = etablissements_query.filter(
            Etablissement.nom.ilike(f"%{query_search}%")
        )
    
    # Limiter les résultats à 10 pour l'autocomplete
    etablissements = etablissements_query.limit(10).all()
    
    # Formater les résultats
    results = []
    for etab in etablissements:
        results.append({
            "id_etab": etab.id_etab,
            "nom": etab.nom,
            "adresse": etab.adresse,
            "ville": etab.ville,
            "code_postal": etab.code_postal,
            "latitude": etab.latitude,
            "longitude": etab.longitude,
            "google_place_id": etab.google_place_id,
            "url": f"/etablissement/{etab.id_etab}"
        })
    
    return jsonify(results)


@etablissements_api_bp.route("/nearby", methods=["GET"])
def get_nearby_etablissements():
    """Retourne les établissements à proximité d'une localisation.
    
    Args:
        lat (float): Latitude
        lng (float): Longitude
        radius (float): Rayon en kilomètres (par défaut: 5km)
        
    Returns:
        JSON: Liste des établissements à proximité
    """
    try:
        lat = float(request.args.get("lat", 0))
        lng = float(request.args.get("lng", 0))
        radius = float(request.args.get("radius", 5))  # 5km par défaut
        
        # Calculer les limites de la boîte de recherche
        # (simplification: 1 degré ≈ 111 km)
        lat_delta = radius / 111.0
        lng_delta = radius / (111.0 * abs(math.cos(math.radians(lat))))
        
        etablissements = Etablissement.query.filter(
            Etablissement.latitude.between(lat - lat_delta, lat + lat_delta),
            Etablissement.longitude.between(lng - lng_delta, lng + lng_delta)
        ).limit(20).all()
        
        results = []
        for etab in etablissements:
            results.append({
                "id_etab": etab.id_etab,
                "nom": etab.nom,
                "adresse": etab.adresse,
                "ville": etab.ville,
                "distance": calculate_distance(lat, lng, etab.latitude, etab.longitude),
                "url": f"/etablissement/{etab.id_etab}"
            })
        
        return jsonify(results)
        
    except ValueError as e:
        return jsonify({"error": "Paramètres invalides"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points en kilomètres (formule de Haversine)."""
    import math
    
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Convertir les degrés en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c
