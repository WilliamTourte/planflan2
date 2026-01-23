#!/usr/bin/env python3
"""
Script pour mettre à jour les templates HTML pour utiliser le nouveau système modulaire JavaScript.

Ce script effectue les modifications suivantes :
1. Ajoute l'attribut data-page-type aux templates
2. Remplace les anciens scripts par le nouveau module main.js
3. Supprime les scripts spécifiques qui sont maintenant intégrés dans les modules
"""

import os
import re
from pathlib import Path

# Configuration des chemins
TEMPLATES_DIR = "app/templates"
SCRIPTS_TO_REMOVE = [
    "liste_etablissements.js",
    "proposer_etablissement.js", 
    "dashboard.js",
    "index.js",
    "map_filter.js"
]

# Mappings des types de pages
PAGE_TYPES = {
    "index.html": "home",
    "liste_etablissements.html": "liste_etablissements",
    "proposer_etablissement.html": "proposer_etablissement",
    "dashboard.html": "dashboard"
}

def update_template_file(file_path, page_type):
    """
    Met à jour un fichier template avec les modifications nécessaires.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 1. Ajouter l'attribut data-page-type
        if page_type:
            # Vérifier si l'attribut est déjà présent
            if 'data-page-type' not in content:
                # Trouver la balise body et ajouter l'attribut
                content = re.sub(
                    r'<body([^>]*)>',
                    f'<body data-page-type="{page_type}"\\1>',
                    content,
                    count=1
                )
                print(f"✓ Ajouté data-page-type='{page_type}' à {file_path.name}")
        
        # 2. Remplacer les anciens scripts par le nouveau module main.js
        # Trouver les scripts à supprimer
        scripts_found = []
        for script in SCRIPTS_TO_REMOVE:
            if f'js/{script}' in content:
                scripts_found.append(script)
                # Supprimer le script
                content = re.sub(
                    rf'<script src="{{{{ url_for\(\'static\', filename=\'js/{script}\'\) }}}}" nonce="{{{{ csp_nonce }}}}"></script>\n?',
                    f'<!-- Le script {script} n\'est plus nécessaire, tout est géré par main.js -->\n',
                    content
                )
                print(f"✓ Supprimé {script} de {file_path.name}")
        
        # 3. Vérifier que le nouveau module main.js est chargé
        if '<script type="module" src="{{ url_for(\'static\', filename=\'js/main.js\') }}"></script>' not in content:
            # Ajouter le nouveau script avant la fin du body
            content = re.sub(
                r'(<script[^>]*src="{{ url_for\(\'static\', filename=\'js/base\.js\'\) }}"[^>]*></script>)\n?',
                r'\\1\n    <script type="module" src="{{ url_for(\'static\', filename=\'js/main.js\') }}"></script>\n',
                content
            )
            print(f"✓ Ajouté le module main.js à {file_path.name}")
        
        # Écrire les modifications
        file_path.write_text(content, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la mise à jour de {file_path.name}: {e}")
        return False

def main():
    """
    Fonction principale pour exécuter les mises à jour.
    """
    print("Début de la mise à jour des templates pour le nouveau système JavaScript...")
    print("=" * 70)
    
    templates_dir = Path(TEMPLATES_DIR)
    
    # Parcourir tous les fichiers HTML dans le dossier templates
    html_files = templates_dir.glob('*.html')
    
    for html_file in html_files:
        # Déterminer le type de page
        page_type = PAGE_TYPES.get(html_file.name, None)
        
        if page_type:
            print(f"\nTraitement de {html_file.name} (type: {page_type})...")
            update_template_file(html_file, page_type)
        else:
            print(f"\nTraitement de {html_file.name} (type: default)...")
            update_template_file(html_file, "default")
    
    print("\n" + "=" * 70)
    print("Mise à jour des templates terminée!")
    print("\nModifications apportées:")
    print("1. Ajout de l'attribut data-page-type sur les balises <body>")
    print("2. Suppression des anciens scripts JavaScript spécifiques")
    print("3. Ajout du nouveau module main.js")
    print("\nVeuillez vérifier les fichiers modifiés et tester l'application.")

if __name__ == "__main__":
    main()