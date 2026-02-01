#!/usr/bin/env python3
"""
Script autonome pour extraire les données des villes françaises depuis un fichier local.

Ce script:
1. Lit les données depuis le fichier local communes-france-full.json
2. Extrait les informations nécessaires (nom, latitude, longitude, population)
3. Génère un fichier JSON avec les données des villes

Utilisation:
    python scripts/get_villes_list.py

Options:
    --limit N      Limite à N villes (pour les tests)
    --output DIR   Répertoire de sortie (défaut: app/data)
"""

import argparse
import json
import os
from typing import List, Dict


def load_villes_data(file_path: str) -> Dict:
    """Charge les données des villes depuis un fichier local."""
    print(f"📥 Chargement des données des villes depuis {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        raise


def extract_relevant_data(raw_data: Dict) -> List[Dict]:
    """Extrait les informations pertinentes des données brutes."""
    print("🔍 Extraction des données pertinentes...")
    villes = []

    # Les données sont dans raw_data['data']
    communes = raw_data.get("data", [])

    for commune in communes:
        # Extraire les coordonnées GPS (latitude et longitude du centre)
        latitude = commune.get("latitude_centre")
        longitude = commune.get("longitude_centre")

        # Si les coordonnées du centre ne sont pas disponibles, utiliser celles de la mairie
        if latitude is None or longitude is None:
            latitude = commune.get("latitude_mairie")
            longitude = commune.get("longitude_mairie")

        # Utiliser le nom standard
        nom = commune.get("nom_standard", "")

        # Extraire la population
        population = commune.get("population")

        # Filtrer les données incomplètes
        if (
            nom
            and latitude is not None
            and longitude is not None
            and population is not None
        ):
            villes.append(
                {
                    "nom": nom,
                    "latitude": latitude,
                    "longitude": longitude,
                    "population": population,
                }
            )

    print(f"✅ {len(villes)} villes extraites")
    return villes


def save_data(villes: List[Dict], output_dir: str):
    """Sauvegarde les données dans des fichiers."""
    print(f"💾 Sauvegarde des données dans {output_dir}...")

    os.makedirs(output_dir, exist_ok=True)

    # Sauvegarder les données des villes
    output_path = os.path.join(output_dir, "villes_autocomplete.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(villes, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier sauvegardé: {output_path}")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Extraire les données des villes françaises depuis un fichier local."
    )
    parser.add_argument(
        "--limit", type=int, help="Limite le nombre de villes à traiter"
    )
    parser.add_argument("--output", default="app/data", help="Répertoire de sortie")

    args = parser.parse_args()

    print("🚀 Début du traitement des données des villes")
    print("=" * 60)

    try:
        # Chemin du fichier source
        input_file = "app/data/communes-france-full.json"

        # Étape 1: Chargement
        raw_data = load_villes_data(input_file)

        # Étape 2: Extraction
        villes = extract_relevant_data(raw_data)

        # Limiter si demandé
        if args.limit:
            villes = villes[: args.limit]
            print(f"📏 Traitement limité à {args.limit} villes")

        # Étape 3: Sauvegarde
        save_data(villes, args.output)

        print("\n✅ Traitement terminé avec succès!")
        print(f"📁 Fichiers sauvegardés dans {args.output}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
