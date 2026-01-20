"""Module utilitaire contenant des fonctions diverses pour l'application PlanFlan.

Ce module regroupe des fonctions utilitaires utilisées dans différentes parties
de l'application, notamment pour le traitement de texte, la vérification CSRF,
et le calcul de distances géographiques.
"""

import requests
import os
from math import radians, sin, cos, sqrt, atan2
from flask import request, current_app
from flask_wtf.csrf import validate_csrf


def enlever_accents(
    text,
):  # Enlève les accents parce que la police ne les gère pas bien
    """Enlève les accents d'un texte.

    Cette fonction est utilisée pour normaliser les textes contenant des accents,
    notamment pour l'affichage avec des polices qui ne gèrent pas bien les accents.

    Args:
        text (str): Le texte à traiter

    Returns:
        str: Le texte sans accents, ou une chaîne vide si text est None
    """
    import unicodedata

    if text is None:
        return ""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")


def verifier_csrf_token():
    """
    Vérifie le token CSRF pour les requêtes API et formulaires.

    Cette fonction vérifie le token CSRF dans l'en-tête X-CSRFToken (pour les requêtes AJAX)
    ou dans le formulaire (pour les requêtes POST classiques).

    Pour les méthodes POST, PUT, DELETE, la vérification CSRF est obligatoire.

    Returns:
        tuple: (bool, str) - (True, None) si le token est valide, (False, message_erreur) sinon
    """
    # #region agent log
    import json

    with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A",
                    "location": "outils.py:36",
                    "message": "verifier_csrf_token entry",
                    "data": {"method": request.method, "path": request.path},
                    "timestamp": int(__import__("time").time() * 1000),
                }
            )
            + "\n"
        )
    # #endregion

    # Pour les méthodes GET, HEAD, OPTIONS, la vérification CSRF n'est pas requise
    if request.method in ("GET", "HEAD", "OPTIONS"):
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A",
                        "location": "outils.py:50",
                        "message": "verifier_csrf_token GET/HEAD/OPTIONS - returning True",
                        "data": {"method": request.method},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return True, None

    # Si nous sommes en environnement de test, désactiver la vérification CSRF
    if hasattr(current_app, "config") and current_app.config.get("TESTING", False):
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A",
                        "location": "outils.py:51",
                        "message": "verifier_csrf_token - TESTING mode, skipping CSRF check",
                        "data": {"method": request.method},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return True, None

    # Pour POST, PUT, DELETE, la vérification CSRF est obligatoire
    # Extraire le token CSRF de l'en-tête ou du formulaire
    csrf_token = request.headers.get("X-CSRFToken") or request.form.get("csrf_token")

    # #region agent log
    with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A",
                    "location": "outils.py:54",
                    "message": "verifier_csrf_token POST/PUT/DELETE - token check",
                    "data": {"method": request.method, "has_token": bool(csrf_token)},
                    "timestamp": int(__import__("time").time() * 1000),
                }
            )
            + "\n"
        )
    # #endregion

    if not csrf_token:
        # Si aucun token n'est fourni pour une méthode qui en nécessite un, c'est une erreur
        current_app.logger.warning(
            f"Token CSRF manquant pour la méthode {request.method} sur {request.path}"
        )
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A",
                        "location": "outils.py:61",
                        "message": "verifier_csrf_token - no token, returning False",
                        "data": {"method": request.method},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return False, "Token CSRF manquant. Veuillez recharger la page et réessayer."

    try:
        validate_csrf(csrf_token)
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A",
                        "location": "outils.py:65",
                        "message": "verifier_csrf_token - token valid, returning True",
                        "data": {},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return True, None
    except Exception as e:
        current_app.logger.warning(f"Token CSRF invalide: {e}")
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A",
                        "location": "outils.py:68",
                        "message": "verifier_csrf_token - token invalid, returning False",
                        "data": {"error": str(e)},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return False, "Token CSRF invalide"


def verifier_csrf_ou_renvoyer_erreur():
    """
    Vérifie le token CSRF et renvoie une réponse d'erreur JSON si invalide.

    Cette fonction est conçue pour être utilisée dans les routes API.

    Returns:
        tuple: (bool, Response) - (True, None) si le token est valide,
        (False, response_erreur) si le token est invalide
    """
    # #region agent log
    import json

    with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B",
                    "location": "outils.py:71",
                    "message": "verifier_csrf_ou_renvoyer_erreur entry",
                    "data": {"method": request.method},
                    "timestamp": int(__import__("time").time() * 1000),
                }
            )
            + "\n"
        )
    # #endregion

    csrf_valide, message = verifier_csrf_token()

    # #region agent log
    with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B",
                    "location": "outils.py:82",
                    "message": "verifier_csrf_ou_renvoyer_erreur - after verifier_csrf_token",
                    "data": {"csrf_valide": csrf_valide, "has_message": bool(message)},
                    "timestamp": int(__import__("time").time() * 1000),
                }
            )
            + "\n"
        )
    # #endregion

    if not csrf_valide:
        from flask import jsonify

        # Always return a 2-tuple: (bool, Response)
        error_response = jsonify({"error": message}), 403
        # #region agent log
        with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "B",
                        "location": "outils.py:85",
                        "message": "verifier_csrf_ou_renvoyer_erreur - returning 2-tuple False",
                        "data": {"response_type": str(type(error_response))},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
        # #endregion
        return False, error_response
    # #region agent log
    with open("/home/damien/PlanFlan/planflan2/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B",
                    "location": "outils.py:86",
                    "message": "verifier_csrf_ou_renvoyer_erreur - returning 2-tuple True",
                    "data": {},
                    "timestamp": int(__import__("time").time() * 1000),
                }
            )
            + "\n"
        )
    # #endregion
    return True, None


def afficher_etablissements(resultats):
    """Convertit les résultats de recherche en listes d'établissements et JSON.

    Args:
        resultats: Les résultats de recherche contenant des établissements

    Returns:
        tuple: (list, list) - Une liste d'objets établissement et une liste de dictionnaires JSON
    """
    etablissements = []
    etablissements_json = []
    for etab in resultats:
        etablissements.append(etab)
        etablissements_json.append(etab.to_dict(include_flans=True))
    return etablissements, etablissements_json


def calculer_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points géographiques en kilomètres.

    Cette fonction utilise la formule de Haversine pour calculer la distance
    entre deux points définis par leurs coordonnées latitude/longitude.

    Args:
        lat1 (float): Latitude du premier point
        lon1 (float): Longitude du premier point
        lat2 (float): Latitude du deuxième point
        lon2 (float): Longitude du deuxième point

    Returns:
        float: La distance en kilomètres entre les deux points
    """
    R = 6371.0
    # Convertir toutes les valeurs en float avant de les convertir en radians
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_place_details(place_id, api_key):
    """
    Récupère les détails d'un lieu depuis l'API Google Places.

    Args:
        place_id (str): Identifiant du lieu dans Google Places
        api_key (str): Clé API Google Places

    Returns:
        dict: Les détails du lieu, ou None en cas d'erreur
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "photos", "key": api_key}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("result"):
                return data["result"]
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des détails: {e}")

    return None


def fetch_place_photos(etablissement_id, place_id, api_key, max_width=400):
    """
    Récupère les photos pour un établissement depuis l'API Google Places et les sauvegarde localement.

    Args:
        etablissement_id (int): Identifiant de l'établissement dans la base de données
        place_id (str): Identifiant Google Places du lieu
        api_key (str): Clé API Google Places
        max_width (int): Largeur maximale des photos (par défaut 400)

    Returns:
        list: Liste des chemins des photos sauvegardées localement
    """
    # Importer les modules nécessaires localement pour éviter les imports circulaires
    from app.models import Photo, TypeCible
    from app import db

    # Vérifier si des photos existent déjà pour cet établissement
    existing_photos = Photo.query.filter_by(id_etab=etablissement_id).all()
    if existing_photos:
        return [photo.path for photo in existing_photos]

    # Récupérer les détails de l'établissement pour obtenir les photoreferences
    # Utiliser le place_id Google Places pour récupérer les photos
    if not place_id:
        current_app.logger.warning(
            f"Aucun place_id fourni pour l'établissement {etablissement_id}"
        )
        return []

    place_details = get_place_details(place_id, api_key)
    if not place_details or "photos" not in place_details:
        return []

    # Récupérer les photos depuis l'API
    photo_paths = []
    for idx, photo in enumerate(place_details["photos"][:1]):  # Limiter à une photo
        photo_reference = photo["photo_reference"]
        url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
            "maxwidth": max_width,
            "photoreference": photo_reference,
            "key": api_key,
        }

        try:
            response = requests.get(url, params=params, stream=True)
            if response.status_code == 200:
                # Générer un nom de fichier unique
                filename = f"etab_{etablissement_id}_photo_{idx}.jpg"
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

                # Sauvegarder la photo localement
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                # Enregistrer la photo dans la base de données
                new_photo = Photo(
                    id_etab=etablissement_id,
                    type_cible=TypeCible.ETABLISSEMENT,
                    path=filepath,
                    largeur=max_width,
                    hauteur=max_width,  # Supposons des photos carrées pour simplifier
                )
                db.session.add(new_photo)
                photo_paths.append(filepath)
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la récupération de la photo: {e}")

    db.session.commit()
    return photo_paths
