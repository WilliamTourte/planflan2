#!/usr/bin/env python3

import os
import re
from collections import defaultdict

def extract_css_classes():
    """Extraire toutes les classes CSS du fichier style.css"""
    css_file = "app/static/css/style.css"
    
    with open(css_file, 'r') as f:
        content = f.read()
    
    # Trouver toutes les définitions de classes
    pattern = r'\.([a-zA-Z0-9_-]+)'
    classes = set(re.findall(pattern, content))
    
    # Filtrer les classes qui sont clairement des valeurs (comme "1rem", "2em", etc.)
    valid_classes = []
    for cls in classes:
        # Exclure les classes qui sont juste des nombres ou des unités CSS
        if not re.match(r'^\d+[a-z]{2}$|^\d+$|^\d+rem$|^\d+s$|^\d+em$', cls):
            valid_classes.append(cls)
    
    return sorted(valid_classes)

def count_class_usage_simple():
    """Compter l'utilisation des classes CSS dans les fichiers HTML"""
    css_classes = extract_css_classes()
    class_usage = defaultdict(int)
    
    # Parcourir tous les fichiers HTML
    html_dir = "app/templates"
    
    for root, dirs, files in os.walk(html_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Trouver tous les attributs class
                        pattern = r'class="([^"]*)"'
                        matches = re.findall(pattern, content)
                        
                        for match in matches:
                            # Diviser les classes et compter chacune
                            classes_in_match = match.split()
                            for class_name in classes_in_match:
                                if class_name in css_classes:
                                    class_usage[class_name] += 1
                                    
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
    print(f"CLASSES ORPHELINES (1 utilisation): {sum(1 for cls in used_classes if class_usage[cls] == 1)}")
    print(f"CLASSES UTILISEES (>1 utilisation): {sum(1 for cls in used_classes if class_usage[cls] > 1)}")
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