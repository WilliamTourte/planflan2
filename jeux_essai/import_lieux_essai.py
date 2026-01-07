import re
import json
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Ajouter le chemin du projet pour importer le module app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

# Configuration pour SQLAlchemy direct (pour les fonctions d'import)
DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://flask_user:flanflask@localhost/planflan_db")

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
    if not os.path.exists(fichier_json):
        print(f"❌ Fichier introuvable : {fichier_json}")
        return
    with app.app_context():
        try:
            # Utiliser le modèle principal Etablissement
            from app.models import Etablissement
            
            with open(fichier_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"📊 Nombre de lieux : {len(data.get('features', []))}")
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
                        else:
                            print(f"⚠️ Déjà présent : {nom}")
                    except Exception as e:
                        print(
                            f"❌ Erreur sur {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}"
                        )
            db.session.commit()
            print("🎉 Import terminé !")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur globale : {e}")


if __name__ == "__main__":
    print("🔧 Exécution en mode complètement standalone...")
    
    # Chemin par défaut dans le dossier jeux_essai
    dossier_jeux_essai = os.path.dirname(os.path.abspath(__file__))
    chemin_par_defaut = os.path.join(dossier_jeux_essai, "lieux_test.json")
    
    # Vérifier si un chemin de fichier est fourni en argument
    if len(sys.argv) > 1:
        fichier_json = sys.argv[1]
    else:
        fichier_json = chemin_par_defaut
        print(f"📝 Aucun fichier spécifié, recherche dans le dossier jeux_essai : {fichier_json}")
        print("   Pour spécifier un autre fichier : python import_lieux_essai.py chemin/vers/fichier.json")
    
    # Vérifications supplémentaires
    print(f"🔍 Vérification du fichier : {fichier_json}")
    print(f"   Existe : {os.path.exists(fichier_json)}")
    if os.path.exists(fichier_json):
        print(f"   Taille : {os.path.getsize(fichier_json)} octets")
        print("✅ Fichier trouvé, début de l'import...")
    else:
        print("   ❌ Fichier introuvable !")
        print("   Vérifiez que :")
        print(f"   1. Le fichier 'lieux_test.json' existe dans le dossier jeux_essai")
        print(f"   2. Le chemin est : {fichier_json}")
        print(f"   3. Vous pouvez spécifier un autre chemin en argument")
        sys.exit(1)
        
    # Exécuter l'import
    importer_lieux(fichier_json)
