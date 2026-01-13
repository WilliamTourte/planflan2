#!/usr/bin/env python3
"""
Script pour mettre à jour les google_place_id dans la base de données
a partir du fichier lieux_test_with_place_ids.json
"""

import os
import json
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Configuration du chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

# Configuration pour SQLAlchemy
DATABASE_URI = os.getenv(
    "DATABASE_URL", "mysql+pymysql://flask_user:flanflask@localhost/planflan_db"
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("update_place_ids_db.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Import de l'application Flask
from app import create_app, db

# Créer l'instance de l'application
app = create_app()


def nettoyer_adresse(adresse):
    """Nettoie l'adresse pour la comparaison"""
    return adresse.split(",")[0].strip()


def extraire_code_postal(adresse):
    """Extrait le code postal de l'adresse"""
    import re

    match = re.search(r"(\d{5})", adresse)
    return match.group(1) if match else None


def extraire_ville(adresse):
    """Extrait la ville de l'adresse"""
    import re

    match = re.search(r"\d{5}\s+([^,]+)", adresse)
    return match.group(1).strip() if match else None


def mettre_a_jour_google_place_ids(fichier_json):
    """
    Met à jour les google_place_id dans la base de données
    """
    logger.info(
        "🚀 Début de la mise à jour des google_place_id dans la base de données"
    )

    if not os.path.exists(fichier_json):
        logger.error(f"❌ Fichier introuvable : {fichier_json}")
        return False

    with app.app_context():
        try:
            # Importer le modèle Etablissement
            from app.models import Etablissement

            # Charger les données du fichier JSON
            with open(fichier_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(
                f"📊 Nombre d'établissements dans le fichier : {len(data.get('features', []))}"
            )

            etablissements_mis_a_jour = 0
            etablissements_deja_a_jour = 0
            etablissements_non_trouves = 0

            for feature in data["features"]:
                try:
                    # Extraire les informations
                    properties = feature["properties"]
                    location = properties["location"]
                    nom = location["name"]
                    adresse_complete = location["address"]
                    google_place_id = properties.get("google_place_id")

                    if not google_place_id:
                        logger.warning(
                            f"⚠️ Aucun google_place_id pour {nom}, passage au suivant"
                        )
                        continue

                    # Nettoyer l'adresse pour la recherche
                    adresse = nettoyer_adresse(adresse_complete)
                    code_postal = extraire_code_postal(adresse_complete)
                    ville = extraire_ville(adresse_complete)

                    # Rechercher l'établissement dans la base de données
                    etablissement = Etablissement.query.filter_by(
                        nom=nom, adresse=adresse
                    ).first()

                    if etablissement:
                        # Vérifier si le google_place_id est déjà défini
                        if etablissement.google_place_id == google_place_id:
                            logger.info(
                                f"✓ Déjà à jour : {nom} (ID: {google_place_id})"
                            )
                            etablissements_deja_a_jour += 1
                        else:
                            # Mettre à jour le google_place_id
                            etablissement.google_place_id = google_place_id
                            db.session.add(etablissement)
                            logger.info(
                                f"✅ Mis à jour : {nom} (ID: {google_place_id})"
                            )
                            etablissements_mis_a_jour += 1
                    else:
                        logger.warning(
                            f"⚠️ Non trouvé dans la base : {nom} (adresse: {adresse})"
                        )
                        etablissements_non_trouves += 1

                except Exception as e:
                    logger.error(
                        f"❌ Erreur pour {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}"
                    )

            # Commit des changements
            if etablissements_mis_a_jour > 0:
                db.session.commit()
                logger.info(
                    f"💾 Commit effectué pour {etablissements_mis_a_jour} établissements"
                )

            # Résumé
            logger.info(f"📊 Résumé de la mise à jour:")
            logger.info(f"   - Établissements mis à jour: {etablissements_mis_a_jour}")
            logger.info(f"   - Déjà à jour: {etablissements_deja_a_jour}")
            logger.info(f"   - Non trouvés dans la base: {etablissements_non_trouves}")
            logger.info(f"   - Total traité: {len(data.get('features', []))}")

            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erreur globale : {e}")
            return False


def main():
    """
    Fonction principale
    """
    # Chemin du fichier JSON avec les place_ids
    dossier_scripts = os.path.dirname(os.path.abspath(__file__))
    fichier_json = os.path.join(dossier_scripts, "lieux_test_with_place_ids.json")

    logger.info(f"📁 Fichier source: {fichier_json}")

    # Vérifier que le fichier existe
    if not os.path.exists(fichier_json):
        logger.error(f"❌ Le fichier {fichier_json} n'existe pas")
        logger.error("Assurez-vous d'avoir d'abord exécuté get_google_place_ids.py")
        sys.exit(1)

    # Exécuter la mise à jour
    success = mettre_a_jour_google_place_ids(fichier_json)

    if success:
        logger.info("🎉 Mise à jour des google_place_id terminée avec succès !")
    else:
        logger.error("❌ La mise à jour a échoué")
        sys.exit(1)


if __name__ == "__main__":
    main()
