import re
import json
import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    filename="database.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Ajouter le chemin du projet pour importer le module app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

# Configuration pour SQLAlchemy direct (pour les fonctions d'import)
DATABASE_URI = os.getenv(
    "DATABASE_URL", "mysql+pymysql://flask_user:flanflask@localhost/planflan_db"
)

# Import de l'application Flask après avoir configuré le chemin
from app import create_app, db, bcrypt

# Créer l'instance de l'application
app = create_app()


def extraire_code_postal(adresse):
    match = re.search(r"(\d{5})", adresse)
    return match.group(1) if match else None


def extraire_ville(adresse):
    match = re.search(r"\d{5}\s+([^,]+)", adresse)
    return match.group(1).strip() if match else None


def nettoyer_adresse(adresse):
    return adresse.split(",")[0].strip()


def importer_lieux(fichier_json):
    print("🚀 Début de l'import...")
    logger.info("Début de l'import des lieux")
    if not os.path.exists(fichier_json):
        print(f"❌ Fichier introuvable : {fichier_json}")
        logger.error(f"Fichier introuvable : {fichier_json}")
        return
    with app.app_context():
        try:
            # Utiliser le modèle principal Etablissement
            from app.models import Etablissement

            with open(fichier_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"📊 Nombre de lieux : {len(data.get('features', []))}")
                logger.info(
                    f"Nombre de lieux à importer : {len(data.get('features', []))}"
                )
                for feature in data["features"]:
                    try:
                        nom = feature["properties"]["location"]["name"]
                        adresse_complete = feature["properties"]["location"]["address"]
                        longitude = feature["geometry"]["coordinates"][0]
                        latitude = feature["geometry"]["coordinates"][1]
                        adresse = nettoyer_adresse(adresse_complete)
                        code_postal = extraire_code_postal(adresse_complete)
                        ville = extraire_ville(adresse_complete)
                        if not Etablissement.query.filter_by(
                            nom=nom, adresse=adresse
                        ).first():
                            lieu = Etablissement(
                                nom=nom,
                                adresse=adresse,
                                code_postal=code_postal,
                                ville=ville,
                                latitude=latitude,
                                longitude=longitude,
                                type_etab="BOULANGERIE",
                                id_user=1,
                            )
                            db.session.add(lieu)
                            print(f"✅ Ajout : {nom}")
                            logger.info(f"Ajout de l'établissement : {nom}")
                        else:
                            print(f"⚠️ Déjà présent : {nom}")
                            logger.info(f"Établissement déjà présent : {nom}")
                    except Exception as e:
                        print(
                            f"❌ Erreur sur {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}"
                        )
                        logger.error(
                            f"Erreur sur {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}"
                        )
            db.session.commit()
            print("🎉 Import terminé !")
            logger.info("Import terminé avec succès")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur globale : {e}")
            logger.error(f"Erreur globale lors de l'import : {e}")


if __name__ == "__main__":
    print("🔧 Exécution en mode complètement standalone...")
    logger.info("Début de l'exécution en mode standalone")

    # Chemin par défaut dans le dossier scripts
    dossier_scripts = os.path.dirname(os.path.abspath(__file__))
    chemin_par_defaut = os.path.join(dossier_scripts, "lieux_test.json")

    # Vérifier si un chemin de fichier est fourni en argument
    if len(sys.argv) > 1:
        fichier_json = sys.argv[1]
    else:
        fichier_json = chemin_par_defaut
        print(
            f"📝 Aucun fichier spécifié, recherche dans le dossier scripts : {fichier_json}"
        )
        logger.info(
            f"Aucun fichier spécifié, recherche dans le dossier scripts : {fichier_json}"
        )
        print(
            "   Pour spécifier un autre fichier : python import_lieux_essai.py chemin/vers/fichier.json"
        )
        logger.info(
            "Pour spécifier un autre fichier : python import_lieux_essai.py chemin/vers/fichier.json"
        )

    # Vérifications supplémentaires
    print(f"🔍 Vérification du fichier : {fichier_json}")
    logger.info(f"Vérification du fichier : {fichier_json}")
    print(f"   Existe : {os.path.exists(fichier_json)}")
    logger.info(f"Fichier existe : {os.path.exists(fichier_json)}")
    if os.path.exists(fichier_json):
        print(f"   Taille : {os.path.getsize(fichier_json)} octets")
        logger.info(f"Taille du fichier : {os.path.getsize(fichier_json)} octets")
        print("✅ Fichier trouvé, début de l'import...")
        logger.info("Fichier trouvé, début de l'import")
    else:
        print("   ❌ Fichier introuvable !")
        logger.error("Fichier introuvable")
        print("   Vérifiez que :")
        logger.info("Vérifiez que :")
        print(f"   1. Le fichier 'lieux_test.json' existe dans le dossier scripts")
        logger.info(f"1. Le fichier 'lieux_test.json' existe dans le dossier scripts")
        print(f"   2. Le chemin est : {fichier_json}")
        logger.info(f"2. Le chemin est : {fichier_json}")
        print(f"   3. Vous pouvez spécifier un autre chemin en argument")
        logger.info(f"3. Vous pouvez spécifier un autre chemin en argument")
        sys.exit(1)

    # Exécuter l'import
    importer_lieux(fichier_json)
