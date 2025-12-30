#!/usr/bin/env python3
"""
Script pour corriger les tests dans test_forms.py
Remplace l'utilisation de 'app' par 'client'
"""

import re


def main():
    input_file = "tests/test_forms.py"

    with open(input_file, "r") as f:
        content = f.read()

    # Remplacer 'def test_*(app, setup_data):' par 'def test_*(client):'
    content = re.sub(
        r"def test_(\w+)\(app, setup_data\):", r"def test_\1(client):", content
    )

    # Remplacer 'with app.app_context():' par 'with client.application.app_context():'
    content = re.sub(
        r"with app\.app_context\(\):", "with client.application.app_context():", content
    )

    with open(input_file, "w") as f:
        f.write(content)

    print(f"Fichier {input_file} corrigé avec succès")


if __name__ == "__main__":
    main()
