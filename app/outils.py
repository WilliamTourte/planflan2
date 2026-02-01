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

    # Pour les méthodes GET, HEAD, OPTIONS, la vérification CSRF n'est pas requise
    if request.method in ("GET", "HEAD", "OPTIONS"):

        return True, None

    # Si nous sommes en environnement de test, désactiver la vérification CSRF
    if hasattr(current_app, "config") and current_app.config.get("TESTING", False):

        return True, None

    # Pour POST, PUT, DELETE, la vérification CSRF est obligatoire
    # Extraire le token CSRF de l'en-tête ou du formulaire
    csrf_token = request.headers.get("X-CSRFToken") or request.form.get("csrf_token")

    if not csrf_token:
        # Si aucun token n'est fourni pour une méthode qui en nécessite un, c'est une erreur
        current_app.logger.warning(
            f"Token CSRF manquant pour la méthode {request.method} sur {request.path}"
        )
        return False, "Token CSRF manquant. Veuillez recharger la page et réessayer."

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

        # Always return a 2-tuple: (bool, Response)
        error_response = jsonify({"error": message}), 403
        current_app.logger.warning(
            f"CSRF verification failed, returning error response: {message}"
        )
        return False, error_response

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
        current_app.logger.info(f"[get_place_details] Appel API pour place_id={place_id}")
        response = requests.get(url, params=params)
        current_app.logger.info(f"[get_place_details] Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            current_app.logger.info(f"[get_place_details] Réponse JSON status: {data.get('status')}")
            if data.get("result"):
                current_app.logger.info(f"[get_place_details] Résultat obtenu, clés: {list(data['result'].keys())}")
                return data["result"]
            else:
                current_app.logger.warning(f"[get_place_details] Pas de 'result' dans la réponse. Data: {data}")
        else:
            current_app.logger.error(f"[get_place_details] Erreur HTTP: {response.status_code}, Body: {response.text[:200]}")
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

    current_app.logger.info(f"[fetch_place_photos] Début - etab_id={etablissement_id}, place_id={place_id}")

    # Vérifier si des photos existent déjà pour cet établissement
    existing_photos = Photo.query.filter_by(id_etab=etablissement_id).all()
    if existing_photos:
        current_app.logger.info(f"[fetch_place_photos] Photos déjà existantes: {[p.path for p in existing_photos]}")
        return [photo.path for photo in existing_photos]

    # Récupérer les détails de l'établissement pour obtenir les photoreferences
    # Utiliser le place_id Google Places pour récupérer les photos
    if not place_id:
        current_app.logger.warning(
            f"Aucun place_id fourni pour l'établissement {etablissement_id}"
        )
        return []

    current_app.logger.info(f"[fetch_place_photos] Appel get_place_details pour place_id={place_id}")
    place_details = get_place_details(place_id, api_key)
    if not place_details:
        current_app.logger.warning(f"[fetch_place_photos] Aucun détail retourné par get_place_details")
        return []
    if "photos" not in place_details:
        current_app.logger.warning(f"[fetch_place_photos] Pas de photos dans place_details. Clés disponibles: {list(place_details.keys())}")
        return []

    # Récupérer les photos depuis l'API
    photo_paths = []
    current_app.logger.info(f"[fetch_place_photos] Nombre de photos disponibles: {len(place_details['photos'])}")
    for idx, photo in enumerate(place_details["photos"][:1]):  # Limiter à une photo
        photo_reference = photo["photo_reference"]
        current_app.logger.info(f"[fetch_place_photos] Traitement photo {idx}, reference={photo_reference[:20]}...")
        url = "https://maps.googleapis.com/maps/api/place/photo"
        params = {
            "maxwidth": max_width,
            "photoreference": photo_reference,
            "key": api_key,
        }

        response = None  # Initialiser pour éviter les erreurs de référence
        try:
            response = requests.get(url, params=params, stream=True, timeout=10)
            response.raise_for_status()  # Lève une exception pour les codes 4xx/5xx

            if response.status_code == 200:
                # Générer un nom de fichier unique basé sur le Google Place ID
                filename = f"{place_id}_photo_{idx}.jpg"
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

                current_app.logger.info(f"[fetch_place_photos] Sauvegarde photo: {filename}")

                # Sauvegarder la photo localement
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                current_app.logger.info(f"[fetch_place_photos] Photo sauvegardée dans: {filepath}")

                # Récupérer les dimensions réelles de l'image
                try:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        width, height = img.size
                    current_app.logger.info(f"[fetch_place_photos] Dimensions: {width}x{height}")
                except Exception as img_error:
                    current_app.logger.warning(f"Impossible de lire les dimensions de l'image: {img_error}")
                    width, height = max_width, max_width  # Fallback

                # Enregistrer la photo dans la base de données
                # ✅ CORRECTION: Stocke uniquement le nom du fichier, pas le chemin complet
                new_photo = Photo(
                    id_etab=etablissement_id,
                    type_cible=TypeCible.ETABLISSEMENT,
                    path=filename,  # ✅ Uniquement le nom du fichier
                    largeur=width,
                    hauteur=height,
                )
                db.session.add(new_photo)
                current_app.logger.info(f"[fetch_place_photos] Photo ajoutée à la session DB: {filename}")
                photo_paths.append(filepath)
        except requests.exceptions.Timeout:
            current_app.logger.error(
                f"Timeout lors du téléchargement de la photo {idx} pour l'établissement {etablissement_id}"
            )
        except requests.exceptions.HTTPError as http_err:
            if response and response.status_code == 429:
                current_app.logger.error(
                    f"Quota Google Places API dépassé pour l'établissement {etablissement_id}"
                )
            else:
                status_code = response.status_code if response else "Unknown"
                current_app.logger.error(
                    f"Erreur HTTP {status_code} lors de la récupération de la photo: {http_err}"
                )
        except requests.exceptions.RequestException as req_err:
            current_app.logger.error(
                f"Erreur réseau lors de la récupération de la photo {idx}: {req_err}"
            )
        except Exception as e:
            current_app.logger.error(
                f"Erreur inattendue lors de la récupération de la photo {idx}: {e}"
            )

    current_app.logger.info(f"[fetch_place_photos] Commit des {len(photo_paths)} photos en base de données")
    db.session.commit()
    current_app.logger.info(f"[fetch_place_photos] Fin - Photos sauvegardées: {photo_paths}")
    return photo_paths
