#!/usr/bin/env python3
"""
Script pour récupérer les Google Place IDs pour les établissements dans lieux_test.json
et mettre à jour le fichier avec ces IDs.
"""

import os
import json
import requests
import logging
from dotenv import load_dotenv
from time import sleep
import sys

# Configuration
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Chemins des fichiers
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPTS_DIR, "lieux_test.json")
OUTPUT_FILE = os.path.join(SCRIPTS_DIR, "lieux_test_with_place_ids.json")
BACKUP_FILE = os.path.join(SCRIPTS_DIR, "lieux_test.json.backup")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(SCRIPTS_DIR, "get_place_ids.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def get_place_id(name, address):
    """
    Effectue une requête à l'API Google Places Text Search pour obtenir le place_id

    Args:
        name: Nom de l'établissement
        address: Adresse de l'établissement

    Returns:
        str: Le place_id trouvé, ou None si non trouvé ou en cas d'erreur
    """
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    # Construire la requête avec nom et adresse
    query = f"{name} {address}"
    params = {"query": query, "key": GOOGLE_MAPS_API_KEY}

    try:

        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        # Vérifier le statut de la réponse
        if data.get("status") == "OK" and data.get("results"):
            place_id = data["results"][0]["place_id"]

            return place_id
        elif data.get("status") == "ZERO_RESULTS":
            logger.warning(f"Aucun résultat trouvé pour {name}")
            return None
        elif data.get("status") == "OVER_QUERY_LIMIT":
            logger.error("Limite de quota API atteinte")
            return "QUOTA_LIMIT"
        else:
            logger.error(f"Statut API inattendu: {data.get('status')} pour {name}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête pour {name}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON pour {name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue pour {name}: {str(e)}")
        return None


def main():
    """
    Fonction principale pour traiter le fichier JSON et ajouter les place_ids
    """
    logger.info("🚀 Début du traitement pour ajouter les Google Place IDs")

    # Vérifier que la clé API est disponible
    if not GOOGLE_MAPS_API_KEY:
        logger.error("❌ Clé API Google Maps non trouvée dans le .env")
        logger.error("Vérifiez que la variable GOOGLE_MAPS_API_KEY est définie")
        sys.exit(1)

    logger.info(f"✓ Clé API Google Maps chargée")

    # Vérifier que le fichier d'entrée existe
    if not os.path.exists(INPUT_FILE):
        logger.error(f"❌ Fichier introuvable: {INPUT_FILE}")
        sys.exit(1)

    logger.info(f"✓ Fichier d'entrée trouvé: {INPUT_FILE}")

    # Créer un backup du fichier original
    try:
        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)
        os.rename(INPUT_FILE, BACKUP_FILE)
        logger.info(f"✓ Backup créé: {BACKUP_FILE}")
    except Exception as e:
        logger.error(f"❌ Impossible de créer le backup: {str(e)}")
        sys.exit(1)

    # Charger les données depuis le backup
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(
            f"✓ Fichier chargé avec {len(data.get('features', []))} établissements"
        )
    except Exception as e:
        logger.error(f"❌ Impossible de charger le fichier JSON: {str(e)}")
        sys.exit(1)

    # Traiter chaque établissement
    total_etablissements = len(data["features"])
    etablissements_trouves = 0
    etablissements_non_trouves = 0

    for i, feature in enumerate(data["features"]):
        try:
            # Extraire les informations de l'établissement
            properties = feature["properties"]
            location = properties["location"]
            name = location["name"]
            address = location["address"]

            logger.info(f"🔍 Traitement {i+1}/{total_etablissements}: {name}")

            # Récupérer le place_id
            place_id = get_place_id(name, address)

            if place_id == "QUOTA_LIMIT":
                logger.error("🛑 Limite de quota atteinte, arrêt du traitement")
                break
            elif place_id:
                # Ajouter le place_id aux propriétés
                properties["google_place_id"] = place_id
                etablissements_trouves += 1
                logger.info(f"✅ Place ID ajouté: {place_id}")
            else:
                # Marquer comme non trouvé
                properties["google_place_id"] = None
                etablissements_non_trouves += 1
                logger.warning(f"⚠️ Aucun Place ID trouvé pour {name}")

            # Respecter les limites de quota (50 requêtes/seconde max)
            # On fait une pause toutes les 40 requêtes pour être prudent
            if (i + 1) % 40 == 0 and i < total_etablissements - 1:
                logger.info(
                    "⏳ Pause de 3 secondes pour respecter les limites de quota API..."
                )
                sleep(3)

        except KeyError as e:
            logger.error(
                f"❌ Structure JSON inattendue pour l'établissement {i+1}: {str(e)}"
            )
            continue
        except Exception as e:
            logger.error(f"❌ Erreur inattendue pour l'établissement {i+1}: {str(e)}")
            continue

    # Sauvegarder le résultat
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Fichier mis à jour sauvegardé: {OUTPUT_FILE}")
        logger.info(f"📊 Résumé:")
        logger.info(f"   - Établissements traités: {total_etablissements}")
        logger.info(f"   - Place IDs trouvés: {etablissements_trouves}")
        logger.info(f"   - Place IDs non trouvés: {etablissements_non_trouves}")
        logger.info(
            f"   - Taux de succès: {etablissements_trouves/total_etablissements*100:.1f}%"
        )

        # Restaurer le fichier original
        if os.path.exists(INPUT_FILE):
            os.remove(INPUT_FILE)
        os.rename(BACKUP_FILE, INPUT_FILE)
        logger.info(f"✓ Fichier original restauré: {INPUT_FILE}")

    except Exception as e:
        logger.error(f"❌ Impossible de sauvegarder le fichier de sortie: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
