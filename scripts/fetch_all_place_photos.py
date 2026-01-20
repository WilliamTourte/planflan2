#!/usr/bin/env python
"""Script pour récupérer les photos de tous les établissements depuis Google Places.

Ce script parcourt tous les établissements dans la base de données et utilise
la fonction fetch_place_photos pour récupérer et sauvegarder les photos
associées à chaque établissement.
"""

import os
import sys

# Ajouter le chemin du projet au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialiser l'application Flask avant les imports
from app import create_app, db
from app.models import Etablissement
from app.outils import fetch_place_photos


def fetch_photos_for_all_etablissements(api_key):
    """Récupère les photos pour tous les établissements.

    Args:
        api_key (str): Clé API Google Places pour récupérer les photos

    Returns:
        dict: Statistiques sur les photos récupérées
    """
    # Créer l'application Flask avec la configuration de production
    app = create_app(config_class="ConfigProd")

    with app.app_context():
        # Récupérer tous les établissements valides avec un google_place_id
        etablissements = Etablissement.query.filter(
            Etablissement.statut == "VALIDE", Etablissement.google_place_id.isnot(None)
        ).all()

        stats = {
            "total_etablissements": len(etablissements),
            "photos_recuperées": 0,
            "erreurs": 0,
            "etablissements_sans_photos": 0,
        }

        print(
            f"Trouvé {stats['total_etablissements']} établissements valides avec un google_place_id"
        )

        for etablissement in etablissements:
            print(
                f"\nTraitement de l'établissement {etablissement.id_etab}: {etablissement.nom}"
            )
            print(f"Google Place ID: {etablissement.google_place_id}")

            try:
                # Appeler la fonction pour récupérer les photos
                photo_paths = fetch_place_photos(
                    etablissement_id=etablissement.id_etab,
                    place_id=etablissement.google_place_id,
                    api_key=api_key,
                )

                if photo_paths:
                    stats["photos_recuperées"] += len(photo_paths)
                    print(f"✓ {len(photo_paths)} photo(s) récupérée(s): {photo_paths}")
                else:
                    stats["etablissements_sans_photos"] += 1
                    print("✗ Aucun photo récupérée pour cet établissement")

            except Exception as e:
                stats["erreurs"] += 1
                print(f"✗ Erreur lors de la récupération des photos: {e}")
                db.session.rollback()

        # Afficher les statistiques finales
        print("\n" + "=" * 60)
        print("STATISTIQUES FINALES")
        print("=" * 60)
        print(f"Établissements traités: {stats['total_etablissements']}")
        print(f"Photos récupérées: {stats['photos_recuperées']}")
        print(f"Établissements sans photos: {stats['etablissements_sans_photos']}")
        print(f"Erreurs rencontrées: {stats['erreurs']}")

        return stats


if __name__ == "__main__":
    # Vérifier que la clé API est fournie
    if len(sys.argv) < 2:
        print("Usage: python fetch_all_place_photos.py <GOOGLE_PLACES_API_KEY>")
        sys.exit(1)

    api_key = sys.argv[1]

    print("Début de la récupération des photos pour tous les établissements...")
    print(
        "Clé API utilisée:",
        api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else api_key,
    )

    # Exécuter la fonction principale
    stats = fetch_photos_for_all_etablissements(api_key)

    print("\nScript terminé avec succès !")
