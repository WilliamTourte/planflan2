# Documentation Sphinx de PlanFlan

Ce dossier contient la documentation technique de l'application PlanFlan générée avec Sphinx.

## Structure

- `conf.py` : Configuration principale de Sphinx
- `index.rst` : Page d'accueil de la documentation
- `modules.rst` : Documentation des modules de l'application
- `_build/html/` : Documentation générée (après construction)
- `_static/` : Fichiers statiques (CSS, JS)
- `_templates/` : Templates personnalisés

## Génération de la documentation

### Prérequis

- Python 3.8+
- Sphinx installé (`pip install sphinx`)
- Thème Read the Docs (`pip install sphinx-rtd-theme`)

### Construction

Pour générer la documentation :

```bash
# Méthode 1: Utiliser le script batch (Windows)
build_docs.bat

# Méthode 2: Commande manuelle
cd source
sphinx-build -b html . _build/html
```

La documentation générée sera disponible dans `source/_build/html/index.html`.

### Visualisation

Ouvrez `source/_build/html/index.html` dans votre navigateur web pour consulter la documentation.

## Configuration

La configuration Sphinx se trouve dans `conf.py` :

- **Thème** : sphinx_rtd_theme (Read the Docs)
- **Langue** : Français
- **Extensions** : viewcode, napoleon, todo
- **Chemin Python** : Configure pour inclure le dossier `app/`

## Documentation du code

La documentation inclut :

- Structure du projet et architecture
- Description des modules principaux
- Instructions pour générer la documentation
- Index et recherche intégrés

## Mise à jour

Pour mettre à jour la documentation après des modifications du code :

1. Mettre à jour les fichiers `.rst` si nécessaire
2. Exécuter `build_docs.bat` pour regénérer
3. Vérifier les avertissements et erreurs

## Problèmes courants

- **Module non trouvé** : Vérifiez que le chemin Python dans `conf.py` est correct
- **Problèmes de formatage** : Utilisez des titres avec des soulignements de la même longueur
- **Avertissements** : La plupart des avertissements peuvent être ignorés s'ils concernent le formatage