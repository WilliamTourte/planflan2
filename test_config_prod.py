#!/usr/bin/env python3
"""
Script de test de la configuration en production
À exécuter dans le conteneur backend Docker
"""

import os
import sys


def test_config():
    """Teste la configuration de production"""

    print("=" * 70)
    print("TEST DE LA CONFIGURATION PRODUCTION")
    print("=" * 70)
    print()

    # Forcer la config de production
    os.environ["FLASK_CONFIG"] = "ConfigProd"

    try:
        from app import create_app
        from app.models import Etablissement, Photo

        app = create_app()

        with app.app_context():
            print("✓ Application créée avec succès")
            print()

            # Tester les configurations importantes
            print("CONFIGURATION CHARGÉE:")
            print("-" * 70)
            print(f"LOG_LEVEL: {app.config.get('LOG_LEVEL')}")
            print(f"UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
            print(f"Dossier existe: {os.path.exists(app.config.get('UPLOAD_FOLDER', ''))}")
            print(f"Écriture possible: {os.access(app.config.get('UPLOAD_FOLDER', ''), os.W_OK)}")

            # Tester la clé API
            api_key = app.config.get("GOOGLE_MAPS_API_KEY")
            if api_key:
                print(f"GOOGLE_MAPS_API_KEY: {api_key[:10]}... (longueur: {len(api_key)})")
            else:
                print("GOOGLE_MAPS_API_KEY: ✗ NON DÉFINIE")

            print()
            print("BASE DE DONNÉES:")
            print("-" * 70)

            # Statistiques de base
            total_etabs = Etablissement.query.count()
            etabs_with_place_id = Etablissement.query.filter(
                Etablissement.google_place_id.isnot(None)
            ).count()
            total_photos = Photo.query.count()

            print(f"Établissements total: {total_etabs}")
            print(f"Établissements avec google_place_id: {etabs_with_place_id}")
            print(f"Photos en base: {total_photos}")

            # Derniers établissements avec place_id
            print()
            print("DERNIERS ÉTABLISSEMENTS AVEC PLACE_ID:")
            print("-" * 70)
            recent = (
                Etablissement.query.filter(Etablissement.google_place_id.isnot(None))
                .order_by(Etablissement.id_etab.desc())
                .limit(5)
                .all()
            )

            for etab in recent:
                photos_count = Photo.query.filter_by(id_etab=etab.id_etab).count()
                place_id_display = (
                    etab.google_place_id[:30] + "..."
                    if len(etab.google_place_id) > 30
                    else etab.google_place_id
                )
                print(f"  [{etab.id_etab}] {etab.nom[:40]}")
                print(f"      Place ID: {place_id_display}")
                print(f"      Photos: {photos_count}")

                # Vérifier si les photos existent physiquement
                if photos_count > 0:
                    photos = Photo.query.filter_by(id_etab=etab.id_etab).all()
                    for photo in photos:
                        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo.path)
                        exists = os.path.exists(photo_path)
                        symbol = "✓" if exists else "✗"
                        size = os.path.getsize(photo_path) if exists else 0
                        print(f"        {symbol} {photo.path} ({size} octets)")
                print()

            print()
            print("TEST DE CONNECTIVITÉ API GOOGLE:")
            print("-" * 70)

            # Tester la connexion à l'API Google
            try:
                import requests

                # Test simple avec l'API Place Details
                test_place_id = "ChIJN1t_tDeuEmsRUsoyG83frY4"  # Sydney Opera House
                url = "https://maps.googleapis.com/maps/api/place/details/json"
                params = {
                    "place_id": test_place_id,
                    "fields": "name",
                    "key": app.config.get("GOOGLE_MAPS_API_KEY"),
                }

                response = requests.get(url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK":
                        print(f"✓ Connexion à l'API Google Places: OK")
                        print(f"  Test avec Sydney Opera House: {data['result'].get('name')}")
                    else:
                        print(f"✗ API retourne status: {data.get('status')}")
                        print(f"  Message: {data.get('error_message', 'Aucun message')}")
                else:
                    print(f"✗ Erreur HTTP {response.status_code}")
                    print(f"  Response: {response.text[:200]}")

            except Exception as e:
                print(f"✗ Erreur lors du test de l'API: {e}")

            print()
            print("=" * 70)
            print("TEST TERMINÉ")
            print("=" * 70)

    except Exception as e:
        print(f"✗ Erreur lors de la création de l'application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_config()
