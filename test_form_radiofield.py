#!/usr/bin/env python3
"""Test script pour vérifier que les formulaires peuvent être instanciés correctement"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.config import TestConfig
    from app.forms import EtabForm

    print("✓ Imports réussis")

    # Créer une application de test
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        # Tester la création du formulaire
        form = EtabForm()

        # Vérifier que statut_etablissement existe
        if hasattr(form, "statut_etablissement"):
            print("✓ Champ statut_etablissement trouvé dans EtabForm")
        else:
            print("✗ Champ statut_etablissement MANQUANT dans EtabForm")
            sys.exit(1)

        # Vérifier que les anciens champs n'existent plus
        if hasattr(form, "label"):
            print(
                "✗ Champ label TOUJOURS PRÉSENT dans EtabForm (devrait être supprimé)"
            )
            sys.exit(1)
        else:
            print("✓ Champ label correctement supprimé")

        if hasattr(form, "visite"):
            print(
                "✗ Champ visite TOUJOURS PRÉSENT dans EtabForm (devrait être supprimé)"
            )
            sys.exit(1)
        else:
            print("✓ Champ visite correctement supprimé")

        # Tester les choix du RadioField
        choices = form.statut_etablissement.choices
        print(f"✓ Choix du RadioField: {choices}")

        expected_choices = [
            ("non_visite", "Non visité"),
            ("visite", "Visité"),
            ("labellise", "Labellisé"),
        ]
        if choices == expected_choices:
            print("✓ Choix du RadioField corrects")
        else:
            print(
                f"✗ Choix du RadioField incorrects. Attendu: {expected_choices}, Obtenu: {choices}"
            )
            sys.exit(1)

        print("\n=== Tous les tests de formulaire réussis ! ===")

except Exception as e:
    print(f"✗ Erreur: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
