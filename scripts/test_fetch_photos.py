#!/usr/bin/env python
"""Script de test pour fetch_place_photos.

Ce script permet de tester la fonction fetch_place_photos avec un seul établissement
pour vérifier que tout fonctionne correctement avant de lancer le script complet.
"""

import os
import sys

# Ajouter le chemin du projet au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Etablissement
from app.outils import fetch_place_photos

def test_fetch_photos(etablissement_id, api_key):
    """Teste la récupération de photos pour un établissement spécifique.
    
    Args:
        etablissement_id (int): ID de l'établissement à tester
        api_key (str): Clé API Google Places
        
    Returns:
        bool: True si succès, False si échec
    """
    # Créer l'application Flask avec la configuration de production
    app = create_app(config_class='ConfigProd')
    
    with app.app_context():
        # Récupérer l'établissement
        etablissement = db.session.get(Etablissement, etablissement_id)
        
        if not etablissement:
            print(f"❌ Établissement avec ID {etablissement_id} non trouvé")
            return False
            
        if not etablissement.google_place_id:
            print(f"❌ L'établissement {etablissement.nom} n'a pas de google_place_id")
            return False
            
        print(f"Test de récupération de photos pour l'établissement {etablissement.id_etab}: {etablissement.nom}")
        print(f"Google Place ID: {etablissement.google_place_id}")
        print(f"Statut: {etablissement.statut}")
        
        try:
            # Appeler la fonction pour récupérer les photos
            photo_paths = fetch_place_photos(
                etablissement_id=etablissement.id_etab,
                place_id=etablissement.google_place_id,
                api_key=api_key
            )
            
            if photo_paths:
                print(f"✅ Succès ! {len(photo_paths)} photo(s) récupérée(s):")
                for path in photo_paths:
                    print(f"  - {path}")
                return True
            else:
                print("⚠️  Aucun photo récupérée pour cet établissement")
                return True
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des photos: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    # Vérifier les arguments
    if len(sys.argv) < 3:
        print("Usage: python test_fetch_photos.py <ETABLISSEMENT_ID> <GOOGLE_PLACES_API_KEY>")
        print("Exemple: python test_fetch_photos.py 1 AIzaSyD...")
        sys.exit(1)
    
    etablissement_id = int(sys.argv[1])
    api_key = sys.argv[2]
    
    print("Début du test de récupération de photos...")
    print(f"Établissement ID: {etablissement_id}")
    print("Clé API utilisée:", api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else api_key)
    
    # Exécuter le test
    success = test_fetch_photos(etablissement_id, api_key)
    
    if success:
        print("\n✅ Test terminé avec succès !")
    else:
        print("\n❌ Test échoué !")
        sys.exit(1)