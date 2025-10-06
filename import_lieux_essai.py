import re
import json
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuration de l'application Flask en standalone
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/planflan_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Définition des modèles directement dans le script
class Etablissement(db.Model):
    __tablename__ = 'etablissements'
    id_etab = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    code_postal = db.Column(db.String(5), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    type_etab = db.Column(db.String(50), nullable=False)

def extraire_code_postal(adresse):
    match = re.search(r'(\d{5})', adresse)
    return match.group(1) if match else None

def extraire_ville(adresse):
    match = re.search(r'\d{5}\s+([^,]+)', adresse)
    return match.group(1).strip() if match else None

def nettoyer_adresse(adresse):
    return adresse.split(',')[0].strip()

def importer_lieux(fichier_json):
    print("🚀 Début de l'import...")
    if not os.path.exists(fichier_json):
        print(f"❌ Fichier introuvable : {fichier_json}")
        return
    with app.app_context():
        try:
            # Créer toutes les tables si elles n'existent pas
            db.create_all()
            with open(fichier_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📊 Nombre de lieux : {len(data.get('features', []))}")
                for feature in data['features']:
                    try:
                        nom = feature['properties']['location']['name']
                        adresse_complete = feature['properties']['location']['address']
                        longitude = feature['geometry']['coordinates'][0]
                        latitude = feature['geometry']['coordinates'][1]
                        adresse = nettoyer_adresse(adresse_complete)
                        code_postal = extraire_code_postal(adresse_complete)
                        ville = extraire_ville(adresse_complete)
                        if not Etablissement.query.filter_by(nom=nom, adresse=adresse).first():
                            lieu = Etablissement(
                                nom=nom,
                                adresse=adresse,
                                code_postal=code_postal,
                                ville=ville,
                                latitude=latitude,
                                longitude=longitude,
                                type_etab='BOULANGERIE'
                            )
                            db.session.add(lieu)
                            print(f"✅ Ajout : {nom}")
                        else:
                            print(f"⚠️ Déjà présent : {nom}")
                    except Exception as e:
                        print(f"❌ Erreur sur {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}")
            db.session.commit()
            print("🎉 Import terminé !")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur globale : {e}")

if __name__ == '__main__':
    print("🔧 Exécution en mode complètement standalone...")
    importer_lieux(r'C:\Users\dhugonnard2025\Desktop\lieux_test.json')
