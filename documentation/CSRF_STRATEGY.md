# Stratégie de Protection CSRF pour PlanFlan

## Introduction

Ce document décrit la stratégie de protection CSRF (Cross-Site Request Forgery) implémentée dans l'application PlanFlan. La protection CSRF est essentielle pour sécuriser les formulaires et les requêtes API contre les attaques CSRF.

## Configuration Globale

### Activation de la Protection CSRF

La protection CSRF est activée globalement dans l'application via Flask-WTF :

```python
# app/__init__.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ...
    csrf.init_app(app)
    # ...
```

### Configuration pour les Tests

Dans l'environnement de test, la protection CSRF est désactivée pour faciliter les tests automatisés :

```python
# app/config.py
class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Désactivé pour les tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

## Implémentation de la Protection CSRF

### 1. Formulaires HTML (Flask-WTF)

Pour tous les formulaires créés avec Flask-WTF, utilisez systématiquement `{{ form.hidden_tag() }}` :

```html
<!-- Exemple dans les templates -->
<form method="POST" action="/some-route">
    {{ form.hidden_tag() }}  <!-- Cela inclut automatiquement le token CSRF -->
    <!-- Autres champs du formulaire -->
    {{ form.field1() }}
    {{ form.field2() }}
    <button type="submit">Envoyer</button>
</form>
```

**Templates corrigés :**
- `index.html`
- `macros.html` (macro `proposer_flan`)
- `proposer_etablissement.html` (déjà correct)
- `dashboard.html` (formulaire de suppression de compte)
- `upload.html` (formulaire simple sans FlaskForm)

### 2. Formulaires HTML Simples (sans Flask-WTF)

Pour les formulaires qui n'utilisent pas Flask-WTF, ajoutez manuellement le champ CSRF :

```html
<!-- Exemple pour les formulaires simples -->
<form method="POST" action="/some-route">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- Autres champs du formulaire -->
    <button type="submit">Envoyer</button>
</form>
```

### 3. Requêtes AJAX/JavaScript

Pour les requêtes AJAX, incluez le token CSRF dans l'en-tête `X-CSRFToken` :

```javascript
// Exemple dans proposer_etablissement.html
fetch('/verifier_etablissement', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify({ nom: place.name }),
})
```

Assurez-vous que le meta tag CSRF est présent dans les templates qui font des requêtes AJAX :

```html
<!-- Dans la section head des templates -->
<meta name="csrf-token" content="{{ csrf_token() }}">
```

**Templates avec meta tag CSRF :**
- `base.html`
- `index.html`
- `liste_etablissements.html`
- `proposer_etablissement.html`
- `upload.html`

## Protection CSRF dans les Routes

### 1. Routes API (JSON)

Pour les routes API qui acceptent des requêtes POST avec JSON, utilisez la fonction utilitaire `verifier_csrf_ou_renvoyer_erreur()` :

```python
# Exemple dans app/routes/maps.py
from app.outils import verifier_csrf_ou_renvoyer_erreur

@maps_bp.route("/geoloc", methods=["POST"])
def geoloc():
    # Vérifier le token CSRF en utilisant la fonction utilitaire
    csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
    if not csrf_valide:
        return response
    
    # Logique de la route
    try:
        data = request.get_json()
        # ...
```

**Routes API protégées :**

- `/extraire_infos_adresse` (POST)
- `/verifier_etablissement` (POST)

### 2. Routes Formulaires (POST)

Pour les routes qui traitent les soumissions de formulaires, utilisez la fonction utilitaire `verifier_csrf_token()` :

```python
# Exemple dans app/routes/photos.py
from app.outils import verifier_csrf_token

@photos_bp.route("/upload", methods=["POST"])
def upload_file():
    # Vérifier le token CSRF pour les requêtes POST
    csrf_valide, message = verifier_csrf_token()
    if not csrf_valide:
        flash(message or "Token CSRF invalide. Veuillez réessayer.", "danger")
        return redirect(url_for("photos.show_uploads"))
    
    # Logique de la route
    # ...
```

**Routes formulaires protégées :**
- `/upload` (POST)
- `/supprimer_compte` (POST)

### 3. Routes avec Formulaires Flask-WTF

Pour les routes qui utilisent des formulaires Flask-WTF, la protection CSRF est automatique lorsque vous utilisez `form.hidden_tag()` dans le template. Aucune vérification supplémentaire n'est nécessaire dans la route.

**Routes avec formulaires Flask-WTF (protection automatique) :**
- Toutes les routes qui utilisent `EtabForm`, `EvalForm`, `NewFlanForm`, etc.
- Exemples : `/ajouter_etablissement`, `/modifier_etablissement`, `/proposer_flan`, etc.

## Fonctions Utilitaires CSRF

### `verifier_csrf_token()`

```python
from app.outils import verifier_csrf_token

# Vérifie le token CSRF et retourne un tuple (bool, str)
csrf_valide, message = verifier_csrf_token()
if not csrf_valide:
    # Gérer l'erreur CSRF
    return redirect(url_for("some_route", error="csrf"))
```

### `verifier_csrf_ou_renvoyer_erreur()`

```python
from app.outils import verifier_csrf_ou_renvoyer_erreur

# Vérifie le token CSRF et retourne une réponse d'erreur JSON si invalide
csrf_valide, response = verifier_csrf_ou_renvoyer_erreur()
if not csrf_valide:
    return response  # Retourne une réponse JSON avec erreur 403
```

## Bonnes Pratiques

### 1. Toujours utiliser `{{ form.hidden_tag() }}`

Pour tous les formulaires Flask-WTF, utilisez toujours `{{ form.hidden_tag() }}` au lieu d'ajouter manuellement des champs CSRF.

### 2. Inclure le meta tag CSRF pour les requêtes AJAX

Toutes les pages qui font des requêtes AJAX doivent inclure le meta tag CSRF :

```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### 3. Utiliser les fonctions utilitaires pour la vérification

Pour les routes API et les routes personnalisées, utilisez les fonctions utilitaires `verifier_csrf_token()` ou `verifier_csrf_ou_renvoyer_erreur()` au lieu de faire des vérifications manuelles.

### 4. Ne pas désactiver la protection CSRF en production

Assurez-vous que `WTF_CSRF_ENABLED = True` dans la configuration de production.

## Tests CSRF

Des tests spécifiques ont été créés pour vérifier la protection CSRF :

```bash
# Exécuter les tests CSRF
pytest tests/test_csrf.py -v
```

Les tests vérifient :
- La présence des tokens CSRF dans les formulaires
- La présence des meta tags CSRF pour les requêtes AJAX
- Le bon fonctionnement des fonctions utilitaires CSRF
- La protection des routes API et des routes formulaires

## Résolution des Problèmes

### Problème : Token CSRF invalide

Si vous obtenez des erreurs "Token CSRF invalide" :

1. **Vérifiez que le formulaire contient bien `{{ form.hidden_tag() }}`**
2. **Vérifiez que la page contient le meta tag CSRF** pour les requêtes AJAX
3. **Assurez-vous que l'utilisateur est connecté** (la session est nécessaire pour le CSRF)
4. **Vérifiez que vous n'avez pas de cache agressif** qui pourrait servir des pages avec des tokens expirés

### Problème : Les tests échouent avec des erreurs CSRF

Dans les tests, la protection CSRF est désactivée par défaut. Si vous avez besoin de tester avec la protection CSRF activée :

```python
# Dans les tests
def test_with_csrf():
    app = create_app(TestConfig)
    app.config['WTF_CSRF_ENABLED'] = True  # Activer pour ce test spécifique
    # ...
```

## Historique des Changements

### Changements récents (2025)

1. **Standardisation de la protection CSRF** :
   - Création de fonctions utilitaires dans `app/outils.py`
   - Remplacement des vérifications manuelles par des appels aux fonctions utilitaires
   - Correction des templates pour utiliser uniformément `{{ form.hidden_tag() }}`

2. **Ajout de la protection CSRF aux routes manquantes** :
   - `/upload` (POST)

   - `/extraire_infos_adresse` (POST)
   - `/verifier_etablissement` (POST)

3. **Création de tests spécifiques CSRF** :
   - Tests pour les fonctions utilitaires
   - Tests pour les routes API
   - Tests pour les formulaires

## Conclusion

La stratégie CSRF de PlanFlan offre une protection complète contre les attaques CSRF tout en restant flexible et facile à maintenir. En suivant les bonnes pratiques décrites dans ce document, vous pouvez vous assurer que toutes les routes et formulaires sont correctement protégés.

Pour toute question ou problème lié à la protection CSRF, consultez la documentation de Flask-WTF ou contactez l'équipe de développement.
