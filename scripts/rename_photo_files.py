"""Script pour renommer les fichiers photos physiques pour correspondre aux noms dans la base de données.

Ce script renomme les fichiers physiques etab_{id}_photo_X.jpg vers {google_place_id}_photo_X.jpg
en se basant sur les informations de la base de données.

Usage:
    python scripts/rename_photo_files.py [--dry-run]
"""

import os
import sys
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le répertoire parent au path pour permettre les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.config import Config
from app.models import Photo, Etablissement
import argparse

# Parse arguments
parser = argparse.ArgumentParser(
    description="Renommer les fichiers photos pour utiliser google_place_id"
)
parser.add_argument(
    '--dry-run',
    action='store_true',
    help="Affiche les changements sans les appliquer"
)

args = parser.parse_args()

def rename_photo_files(dry_run=False):
    """Renomme les fichiers photos pour utiliser google_place_id."""
    app = create_app(Config)
    
    with app.app_context():
        upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        
        # Lister tous les fichiers dans le dossier uploads
        all_files = os.listdir(upload_folder)
        etab_files = [f for f in all_files if f.startswith('etab_') and f.endswith('.jpg')]
        
        print(f"Fichiers trouvés avec le format 'etab_X': {len(etab_files)}")
        print("-" * 60)
        
        renamed_count = 0
        error_count = 0
        
        for filename in etab_files:
            # Extraire l'id_etab et l'index de la photo
            # Format: etab_105_photo_0.jpg
            parts = filename.replace('.jpg', '').split('_photo_')
            if len(parts) != 2:
                print(f"⚠ Format de fichier non reconnu: {filename}")
                continue
            
            etab_part = parts[0]  # "etab_105"
            photo_index = parts[1]  # "0"
            
            try:
                id_etab = int(etab_part.replace('etab_', ''))
            except ValueError:
                print(f"⚠ ID établissement invalide dans: {filename}")
                continue
            
            # Chercher l'établissement dans la base de données
            etab = Etablissement.query.get(id_etab)
            
            if not etab:
                print(f"⚠ Établissement {id_etab} non trouvé dans la base de données: {filename}")
                error_count += 1
                continue
            
            if not etab.google_place_id:
                print(f"⚠ Pas de google_place_id pour l'établissement {id_etab}: {filename}")
                error_count += 1
                continue
            
            # Construire le nouveau nom de fichier
            new_filename = f"{etab.google_place_id}_photo_{photo_index}.jpg"
            
            old_filepath = os.path.join(upload_folder, filename)
            new_filepath = os.path.join(upload_folder, new_filename)
            
            # Vérifier si le nouveau fichier existe déjà
            if os.path.exists(new_filepath):
                print(f"⚠ Le fichier de destination existe déjà: {new_filename}")
                error_count += 1
                continue
            
            if dry_run:
                print(f"[DRY-RUN] {filename} → {new_filename}")
            else:
                try:
                    os.rename(old_filepath, new_filepath)
                    print(f"✓ {filename} → {new_filename}")
                    renamed_count += 1
                except Exception as e:
                    print(f"✗ Erreur lors du renommage de {filename}: {e}")
                    error_count += 1
        
        print("-" * 60)
        if dry_run:
            print(f"[DRY-RUN] {renamed_count} fichiers seraient renommés")
        else:
            print(f"✓ {renamed_count} fichiers renommés")
        
        if error_count > 0:
            print(f"⚠ {error_count} erreurs rencontrées")


if __name__ == "__main__":
    print("=" * 60)
    print("Script de renommage des fichiers photos")
    print("=" * 60)
    
    if args.dry_run:
        print("[MODE DRY-RUN] Aucun changement ne sera effectué")
        print()
    
    rename_photo_files(dry_run=args.dry_run)
