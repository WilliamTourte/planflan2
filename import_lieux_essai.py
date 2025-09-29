import json
import re
from app import create_app, db
from app.models import Etablissement

app = create_app()
app.app_context().push()

def extraire_code_postal(adresse):
    """Extrait le code postal (ex: 75009)."""
    match = re.search(r'(\d{5})', adresse)
    return match.group(1) if match else None

def extraire_ville(adresse):
    """Extrait la ville (ex: "Paris" ou "Asnières-sur-Seine")."""
    # Cherche un motif comme "75009 Paris" ou "92600 Asnières-sur-Seine"
    match = re.search(r'\d{5}\s+([^,]+)', adresse)
    return match.group(1).strip() if match else None

def nettoyer_adresse(adresse):
    """Garde uniquement le numéro et le nom de la rue (avant la première virgule)."""
    return adresse.split(',')[0].strip()

def importer_lieux_depuis_json(fichier_json):
    with open(fichier_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for feature in data['features']:
        try:
            # Données brutes
            nom = feature['properties']['location']['name']
            adresse_complete = feature['properties']['location']['address']
            longitude = feature['geometry']['coordinates'][0]
            latitude = feature['geometry']['coordinates'][1]

            # Nettoyage et extraction
            adresse = nettoyer_adresse(adresse_complete)
            code_postal = extraire_code_postal(adresse_complete)
            ville = extraire_ville(adresse_complete)

            # Vérification des doublons
            if not Etablissement.query.filter_by(nom=nom, adresse=adresse).first():
                lieu = Etablissement(
                    nom=nom,
                    adresse=adresse,          # Ex: "11 Rue de Châteaudun"
                    code_postal=code_postal,  # Ex: "75009"
                    ville=ville,              # Ex: "Paris"
                    latitude=latitude,
                    longitude=longitude
                )
                db.session.add(lieu)
                print(f"✅ Ajout de {nom} ({adresse}, {code_postal} {ville})")
            else:
                print(f"⚠️ {nom} existe déjà.")

        except Exception as e:
            print(f"❌ Erreur pour {feature['properties']['location'].get('name', 'Inconnu')}: {str(e)}")

    db.session.commit()
    print(f"🎉 Import terminé : {len(data['features'])} lieux traités.")

if __name__ == '__main__':
    importer_lieux_depuis_json(r'C:\Users\dhugonnard2025\Desktop\lieux_test.json')
