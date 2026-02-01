"""Script de migration pour corriger les chemins des photos dans la base de données.

Ce script effectue deux opérations:
1. Retire le préfixe 'uploads/' des paths de photos existants
2. Renomme les fichiers pour utiliser google_place_id au lieu de id_etab (si applicable)

Usage:
    python scripts/fix_photo_paths.py [--dry-run]
    
Options:
    --dry-run  : Affiche les changements sans les appliquer
"""

import os
import sys
import argparse

# Ajouter le répertoire parent au path pour permettre les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Photo, Etablissement


def fix_photo_paths(dry_run=False):
    """Corrige les chemins des photos dans la base de données.
    
    Args:
        dry_run (bool): Si True, affiche les changements sans les appliquer
    """
    app = create_app()
    with app.app_context():
        photos = Photo.query.all()
        total_photos = len(photos)
        corrected_count = 0
        renamed_count = 0
        
        print(f"Traitement de {total_photos} photos...")
        print("-" * 60)
        
        for photo in photos:
            original_path = photo.path
            modified = False
            
            # 1. Retirer le préfixe 'uploads/' si présent
            if photo.path.startswith('uploads/'):
                photo.path = photo.path.replace('uploads/', '', 1)
                modified = True
                corrected_count += 1
                print(f"✓ Correction du préfixe: '{original_path}' -> '{photo.path}'")
            
            # 2. Retirer le préfixe 'static/uploads/' si présent
            if photo.path.startswith('static/uploads/'):
                photo.path = photo.path.replace('static/uploads/', '', 1)
                modified = True
                corrected_count += 1
                print(f"✓ Correction du préfixe: '{original_path}' -> '{photo.path}'")
            
            # 3. Renommer les fichiers etab_{id}_photo_{n}.jpg vers {google_place_id}_photo_{n}.jpg
            if photo.path.startswith('etab_') and photo.id_etab:
                # Récupérer l'établissement associé
                etab = Etablissement.query.get(photo.id_etab)
                if etab and etab.google_place_id:
                    # Extraire le numéro de photo (ex: etab_123_photo_0.jpg -> 0)
                    parts = photo.path.split('_photo_')
                    if len(parts) == 2:
                        photo_index = parts[1]  # Ex: "0.jpg"
                        new_filename = f"{etab.google_place_id}_photo_{photo_index}"
                        
                        # Renommer le fichier physique si nécessaire
                        old_filepath = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), photo.path)
                        new_filepath = os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), new_filename)
                        
                        if os.path.exists(old_filepath):
                            if not dry_run:
                                try:
                                    os.rename(old_filepath, new_filepath)
                                    print(f"✓ Fichier renommé: '{photo.path}' -> '{new_filename}'")
                                except Exception as e:
                                    print(f"✗ Erreur lors du renommage du fichier: {e}")
                                    continue
                            else:
                                print(f"[DRY-RUN] Fichier serait renommé: '{photo.path}' -> '{new_filename}'")
                        
                        photo.path = new_filename
                        modified = True
                        renamed_count += 1
                        
        if not dry_run and (corrected_count > 0 or renamed_count > 0):
            db.session.commit()
            print("-" * 60)
            print(f"✓ {corrected_count} chemins corrigés (préfixes retirés)")
            print(f"✓ {renamed_count} fichiers renommés (google_place_id)")
            print(f"✓ Total: {total_photos} photos traitées")
        elif dry_run:
            print("-" * 60)
            print(f"[DRY-RUN] {corrected_count} chemins seraient corrigés")
            print(f"[DRY-RUN] {renamed_count} fichiers seraient renommés")
            print(f"[DRY-RUN] Total: {total_photos} photos")
        else:
            print("-" * 60)
            print(f"✓ Aucune correction nécessaire sur {total_photos} photos")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script de migration pour corriger les chemins des photos"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Affiche les changements sans les appliquer"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Script de migration des chemins de photos")
    print("=" * 60)
    
    if args.dry_run:
        print("[MODE DRY-RUN] Aucun changement ne sera effectué")
        print()
    
    fix_photo_paths(dry_run=args.dry_run)
