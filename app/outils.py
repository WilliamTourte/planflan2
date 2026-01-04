from math import radians, sin, cos, sqrt, atan2
from flask import request, current_app
from flask_wtf.csrf import validate_csrf


def enlever_accents(
    text,
):  # Enlève les accents parce que la police ne les gère pas bien
    import unicodedata

    if text is None:
        return ""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")


def verifier_csrf_token():
    """
    Vérifie le token CSRF pour les requêtes API et formulaires.
    
    Cette fonction vérifie le token CSRF dans l'en-tête X-CSRFToken (pour les requêtes AJAX)
    ou dans le formulaire (pour les requêtes POST classiques).
    
    Returns:
        tuple: (bool, str) - (True, None) si le token est valide, (False, message_erreur) sinon
    """
    # Extraire le token CSRF de l'en-tête ou du formulaire
    csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
    
    if not csrf_token:
        # Si aucun token n'est fourni, c'est acceptable pour certaines routes
        # (par exemple, les routes GET ou les routes publiques)
        return True, None
    
    try:
        validate_csrf(csrf_token)
        return True, None
    except Exception as e:
        current_app.logger.warning(f"Token CSRF invalide: {e}")
        return False, "Token CSRF invalide"


def verifier_csrf_ou_renvoyer_erreur():
    """
    Vérifie le token CSRF et renvoie une réponse d'erreur JSON si invalide.
    
    Cette fonction est conçue pour être utilisée dans les routes API.
    
    Returns:
        tuple: (bool, Response) - (True, None) si le token est valide, 
        (False, response_erreur) si le token est invalide
    """
    csrf_valide, message = verifier_csrf_token()
    if not csrf_valide:
        from flask import jsonify
        return False, jsonify({"error": message}), 403
    return True, None


def afficher_etablissements(resultats):
    etablissements = []
    etablissements_json = []
    for etab in resultats:
        etablissements.append(etab)
        etablissements_json.append(etab.to_dict(include_flans=True))
    return etablissements, etablissements_json


def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    # Convertir toutes les valeurs en float avant de les convertir en radians
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
