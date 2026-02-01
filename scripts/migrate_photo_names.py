#!/usr/bin/env python
"""Script pour migrer les noms de fichiers photos de l'ancien format vers le nouveau.

Ancien format: etab_{id_etab}_photo_{idx}.jpg
Nouveau format: {google_place_id}_photo_{idx}.jpg
"""

import os
import sys

# Ajouter le chemin du projet au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Photo, Etablissement


def migrate_photo_names():
    """Migre les noms de fichiers photos de l'ancien format vers le nouveau."""
    app = create_app()

    with app.app_context():
        # Récupérer toutes les photos
        photos = (
            Photo.query.join(Etablissement)
            .filter(Etablissement.google_place_id.isnot(None))
            .all()
        )

        stats = {
            "total": len(photos),
            "migrated": 0,
            "errors": 0,
            "skipped": 0,
        }

        print(f"Trouvé {stats['total']} photos à vérifier")

        for photo in photos:
            # Vérifier si la photo utilise l'ancien format
            if not photo.path.startswith("etab_"):
                stats["skipped"] += 1
                continue

            etablissement = db.session.get(Etablissement, photo.id_etab)
            if not etablissement or not etablissement.google_place_id:
                print(
                    f"⚠️  Photo {photo.id_photo}: pas de Google Place ID pour l'établissement {photo.id_etab}"
                )
                stats["errors"] += 1
                continue

            # Extraire l'index de la photo de l'ancien nom
            # Format: etab_{id}_photo_{idx}.jpg
            parts = photo.path.split("_")
            if len(parts) >= 4:
                idx = parts[3].replace(".jpg", "")
                old_filename = photo.path
                new_filename = f"{etablissement.google_place_id}_photo_{idx}.jpg"

                # Chemins complets
                upload_folder = app.config.get("UPLOAD_FOLDER", "app/static/uploads")
                old_filepath = os.path.join(upload_folder, old_filename)
                new_filepath = os.path.join(upload_folder, new_filename)

                try:
                    # Renommer le fichier s'il existe
                    if os.path.exists(old_filepath):
                        os.rename(old_filepath, new_filepath)
                        print(f"✓ Fichier renommé: {old_filename} -> {new_filename}")
                    else:
                        print(f"⚠️  Fichier non trouvé: {old_filepath}")

                    # Mettre à jour la base de données
                    photo.path = new_filename
                    db.session.add(photo)
                    stats["migrated"] += 1

                except Exception as e:
                    print(f"✗ Erreur pour photo {photo.id_photo}: {e}")
                    stats["errors"] += 1
                    db.session.rollback()

        # Commit toutes les modifications
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("MIGRATION TERMINÉE")
            print("=" * 60)
            print(f"Total photos vérifiées: {stats['total']}")
            print(f"Photos migrées: {stats['migrated']}")
            print(f"Photos déjà au bon format: {stats['skipped']}")
            print(f"Erreurs: {stats['errors']}")
        except Exception as e:
            print(f"\n✗ Erreur lors du commit: {e}")
            db.session.rollback()


if __name__ == "__main__":
    migrate_photo_names()
