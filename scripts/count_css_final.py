#!/usr/bin/env python3

import os
import re
from collections import defaultdict

os.chdir("..")


def extract_css_classes():
    """Extraire toutes les classes CSS du fichier style.css"""
    css_file = "app/static/css/style.css"

    with open(css_file, "r") as f:
        content = f.read()

    # Trouver toutes les définitions de classes
    pattern = r"\.([a-zA-Z0-9_-]+)"
    classes = set(re.findall(pattern, content))

    # Filtrer les classes qui sont clairement des valeurs (comme "1rem", "2em", etc.)
    valid_classes = []
    for cls in classes:
        # Exclure les classes qui sont juste des nombres ou des unités CSS
        if not re.match(r"^\d+[a-z]{2}$|^\d+$|^\d+rem$|^\d+s$|^\d+em$", cls):
            valid_classes.append(cls)

    return sorted(valid_classes)


def count_class_usage_simple():
    """Compter l'utilisation des classes CSS dans les fichiers HTML et JS"""
    css_classes = extract_css_classes()
    class_usage = defaultdict(int)

    # Parcourir tous les fichiers HTML et JS dans app/templates et app/static/js
    search_dirs = ["app/templates", "app/static/js"]

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.endswith(".html") or file.endswith(".js"):
                        file_path = os.path.join(root, file)

                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()

                                # Rechercher tous les noms de classes CSS dans le contenu
                                # Cela inclut les classes dans les attributs class="..." et aussi les références directes
                                for class_name in css_classes:
                                    # Rechercher le nom de classe comme mot entier (pour éviter les faux positifs)
                                    # Utiliser une regex pour trouver le nom de classe comme mot séparé
                                    pattern = r"\b" + re.escape(class_name) + r"\b"
                                    matches = re.findall(pattern, content)
                                    if matches:
                                        class_usage[class_name] += len(matches)

                        except (UnicodeDecodeError, PermissionError):
                            continue

    return class_usage


def main():
    """Compter l'utilisation des classes CSS"""
    class_usage = count_class_usage_simple()

    # Extraire toutes les classes pour avoir la liste complète
    all_classes = extract_css_classes()

    print(f"Trouvé {len(all_classes)} classes CSS dans style.css")
    print("=" * 70)

    # Afficher les statistiques
    used_classes = [cls for cls in all_classes if class_usage[cls] > 0]
    unused_classes = [cls for cls in all_classes if class_usage[cls] == 0]

    # Classes utilisées
    print("CLASSES UTILISEES:")
    for class_name in used_classes:
        count = class_usage[class_name]
        status = "ORPHELINE" if count == 1 else f"({count} utilisations)"
        print(f"  {class_name:30} {status}")

    print("\n" + "=" * 70)
    print(f"CLASSES NON UTILISEES ({len(unused_classes)}):")
    for class_name in unused_classes:
        print(f"  {class_name}")

    print("\n" + "=" * 70)
    print(
        f"CLASSES ORPHELINES (1 utilisation): {sum(1 for cls in used_classes if class_usage[cls] == 1)}"
    )
    print(
        f"CLASSES UTILISEES (>1 utilisation): {sum(1 for cls in used_classes if class_usage[cls] > 1)}"
    )
    print(f"CLASSES NON UTILISEES: {len(unused_classes)}")
    print(f"TOTAL CLASSES: {len(all_classes)}")

    # Afficher les classes orphelines
    orphans = [cls for cls in used_classes if class_usage[cls] == 1]
    if orphans:
        print(f"\n" + "=" * 70)
        print("LISTE DES CLASSES ORPHELINES:")
        for class_name in orphans:
            print(f"  {class_name}")


if __name__ == "__main__":
    main()
