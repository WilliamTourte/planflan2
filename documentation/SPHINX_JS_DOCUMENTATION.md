# Documentation JavaScript avec Sphinx

Ce guide explique comment configurer Sphinx pour générer la documentation à la fois pour le code Python et JavaScript dans le projet PlanFlan.

## État actuel

Actuellement, le projet utilise Sphinx pour la documentation Python et une documentation JavaScript manuelle dans `source/javascript.rst`. Les fichiers JavaScript utilisent des commentaires JSDoc qui ne sont pas exploités par Sphinx.

## Objectif

Intégrer la documentation JavaScript dans Sphinx pour avoir une documentation unifiée et automatique pour l'ensemble du projet.

## Solution : Utilisation de sphinx-js

### Étape 1 : Installation de l'extension

L'extension `sphinx-js` permet à Sphinx de parser les commentaires JSDoc et de générer de la documentation au format RST.

```bash
pip install sphinx-js
```

### Étape 2 : Configuration de Sphinx

Modifier `source/conf.py` pour ajouter l'extension et configurer les chemins :

```python
extensions = [
    # Extensions existantes
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinxcontrib.httpdomain",
    
    # Nouvelle extension pour JavaScript
    "sphinx_js",
]

# Configuration pour sphinx-js
js_source_path = "../app/static/js"
jsdoc_config_path = "../jsdoc.conf.json"  # Optionnel
```

### Étape 3 : Configuration JSDoc (optionnel)

Créer un fichier `jsdoc.conf.json` à la racine du projet :

```json
{
  "tags": {
    "allowUnknownTags": true,
    "dictionaries": ["jsdoc", "closure"]
  },
  "source": {
    "include": ["app/static/js"],
    "exclude": ["app/static/js/vendor"]
  },
  "plugins": [],
  "templates": {
    "cleverLinks": false,
    "monospaceLinks": false
  }
}
```

### Étape 4 : Standardisation des commentaires JSDoc

Les fichiers JavaScript doivent utiliser des commentaires JSDoc standardisés :

```javascript
/**
 * Initialise la carte Google Maps.
 * 
 * @function initMap
 * @returns {Promise<void>} Une promesse qui se résout lorsque la carte est initialisée
 * 
 * @example
 * // Appelé automatiquement au chargement de la page
 * initMap();
 */
export function initMap() {
  // Implementation
}
```

### Étape 5 : Intégration dans les fichiers RST

Modifier `source/javascript.rst` pour utiliser les directives sphinx-js :

```rst
Documentation JavaScript
========================

.. js:autodoc:: ../app/static/js/macros.js
   :noindex:

.. js:autodoc:: ../app/static/js/api.js
   :noindex:

.. js:autodoc:: ../app/static/js/utils.js
   :noindex:
```

### Étape 6 : Mise à jour du build de documentation

Modifier `build_docs.bat` pour s'assurer que la documentation JavaScript est incluse.

## Avantages

1. **Documentation unifiée** : Tous les aspects du projet dans un seul endroit
2. **Maintenance simplifiée** : Les commentaires JSDoc servent à la fois pour la documentation et pour l'IDE
3. **Consistance** : Même style de documentation pour Python et JavaScript
4. **Navigation améliorée** : Liens croisés entre les différentes parties du code

## Défis potentiels

1. **Complexité accrue** : Configuration plus complexe de Sphinx
2. **Apprentissage** : Nécessité de maîtriser les conventions JSDoc
3. **Performance** : Génération de documentation potentiellement plus lente

## Exemples de commentaires JSDoc

### Fonction simple

```javascript
/**
 * Calcule la distance entre deux points géographiques.
 * 
 * @param {Object} point1 - Premier point avec lat et lng
 * @param {number} point1.lat - Latitude du premier point
 * @param {number} point1.lng - Longitude du premier point
 * @param {Object} point2 - Deuxième point avec lat et lng
 * @param {number} point2.lat - Latitude du deuxième point
 * @param {number} point2.lng - Longitude du deuxième point
 * @returns {number} Distance en kilomètres
 * 
 * @example
 * const distance = calculateDistance(
 *   {lat: 48.8566, lng: 2.3522},
 *   {lat: 48.8588, lng: 2.3471}
 * );
 */
export function calculateDistance(point1, point2) {
  // Implementation
}
```

### Classe

```javascript
/**
 * Classe représentant un établissement.
 * 
 * @class
 */
export class Etablissement {
  /**
   * Crée une instance d'Etablissement.
   * 
   * @param {number} id - Identifiant unique
   * @param {string} nom - Nom de l'établissement
   * @param {Object} position - Position géographique
   * @param {number} position.lat - Latitude
   * @param {number} position.lng - Longitude
   */
  constructor(id, nom, position) {
    this.id = id;
    this.nom = nom;
    this.position = position;
  }
  
  /**
   * Calcule la distance par rapport à un autre établissement.
   * 
   * @param {Etablissement} other - Autre établissement
   * @returns {number} Distance en kilomètres
   */
  distanceTo(other) {
    // Implementation
  }
}
```

## Bonnes pratiques

1. **Soyez complet** : Documentez tous les paramètres, valeurs de retour et exceptions
2. **Utilisez des exemples** : Les exemples aident les développeurs à comprendre l'utilisation
3. **Soyez cohérent** : Utilisez les mêmes conventions dans tout le code
4. **Mettez à jour** : Mettez à jour la documentation lorsque le code change

## Ressources

- [Documentation sphinx-js](https://github.com/sphinx-contrib/jsmath)
- [Spécification JSDoc](https://jsdoc.app/)
- [Guide JSDoc](https://devhints.io/jsdoc)
