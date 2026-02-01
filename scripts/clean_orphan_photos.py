#!/usr/bin/env python3
"""Script pour nettoyer les entrées photos orphelines (en base mais sans fichier physique).

Ce script parcourt toutes les photos en base de données et supprime celles
dont le fichier physique n'existe pas.
"""

import os
import sys

# Ajouter le chemin du projet au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Photo


def clean_orphan_photos():
    """Nettoie les photos orphelines (en base sans fichier physique)."""

    # Créer l'application avec la config de production
    os.environ["FLASK_CONFIG"] = "ConfigProd"
    app = create_app()

    with app.app_context():
        upload_folder = app.config.get("UPLOAD_FOLDER")

        print("=" * 70)
        print("NETTOYAGE DES PHOTOS ORPHELINES")
        print("=" * 70)
        print(f"UPLOAD_FOLDER: {upload_folder}")
        print()

        # Récupérer toutes les photos
        all_photos = Photo.query.all()
        print(f"Total photos en base: {len(all_photos)}")
        print()

        orphans = []
        valid = []

        for photo in all_photos:
            # Construire le chemin complet
            filepath = os.path.join(upload_folder, photo.path)

            if os.path.exists(filepath):
                valid.append(photo)
            else:
                orphans.append(photo)
                print(
                    f"✗ ORPHELINE: Photo ID {photo.id_photo}, id_etab={photo.id_etab}, path='{photo.path}'"
                )
                print(f"  Fichier attendu: {filepath}")
                print(f"  Fichier existe: False")

        print()
        print("-" * 70)
        print(f"Photos valides (avec fichier): {len(valid)}")
        print(f"Photos orphelines (sans fichier): {len(orphans)}")
        print("-" * 70)
        print()

        if orphans:
            print("PHOTOS ORPHELINES À SUPPRIMER:")
            for photo in orphans:
                print(
                    f"  - ID {photo.id_photo}: {photo.path} (id_etab={photo.id_etab})"
                )
            print()

            response = input(
                f"Supprimer ces {len(orphans)} photo(s) orpheline(s) de la base ? (y/N): "
            )

            if response.lower() == "y":
                for photo in orphans:
                    db.session.delete(photo)
                    print(f"✓ Supprimée: Photo ID {photo.id_photo}")

                db.session.commit()
                print()
                print(
                    f"✅ {len(orphans)} photo(s) orpheline(s) supprimée(s) avec succès"
                )
            else:
                print("❌ Annulé - Aucune photo supprimée")
        else:
            print("✅ Aucune photo orpheline trouvée - Base de données propre !")

        print()
        print("=" * 70)
        print("FIN DU NETTOYAGE")
        print("=" * 70)


if __name__ == "__main__":
    clean_orphan_photos()
