# Analyse des différences entre évaluations, flans et établissements

Ce document détaille les différences dans la logique des évaluations par rapport aux flans et établissements dans l'application PlanFlan.

## Table des matières
- [Structure des templates](#structure-des-templates)
- [Gestion des éditions](#gestion-des-éditions)
- [Routes Flask](#routes-flask)
- [JavaScript](#javascript)
- [Différences clés](#différences-clés)

## Structure des templates

### Pages principales
- **Évaluations** : `page_evaluation.html`
- **Flans** : `page_flan.html`
- **Établissements** : `page_etablissement.html`

### Layout spécifique

#### Évaluations
- Layout en 2 colonnes avec image de flan par défaut à gauche
- Détails à droite incluant :
  - Nom de l'établissement et du flan
  - Date de création
  - 4 critères d'évaluation (visuel, pâte, texture, goût)
  - Moyenne calculée
  - Badge de statut (validé)

#### Flans
- Layout similaire mais avec :
  - Image spécifique du flan
  - Attributs détaillés (saveur, pâte, texture, prix)
  - Moyenne des évaluations associées
  - Lien vers l'établissement parent

#### Établissements
- Layout avec :
  - Image de l'établissement
  - Badge de type (BOULANGERIE, PATISSERIE, etc.)
  - Badge labellisé si applicable
  - Nombre de flans proposés
  - Coordonnées complètes

### Navigation

- **Évaluations** : 
  - Bouton retour vers le flan parent
  - Lien direct vers le flan
  - Fallback vers la page du flan

- **Flans** :
  - Bouton retour vers l'établissement parent
  - Lien direct vers l'établissement
  - Fallback vers la page de l'établissement

- **Établissements** :
  - Bouton retour vers la carte
  - Lien vers la carte
  - Fallback vers la liste des établissements

## Gestion des éditions

### Formulaires d'édition

#### Évaluations
- 4 champs de notation (1-5) :
  - Visuel
  - Pâte
  - Texture
  - Goût
- Champ description optionnel
- Formulaire préfixé avec "eval-detail"

#### Flans
- Champs :
  - Nom
  - Prix
  - Type de pâte (enum)
  - Type de saveur (enum)
  - Type de texture (enum)

#### Établissements
- Champs :
  - Nom
  - Adresse
  - Ville
  - Code postal
  - Latitude
  - Longitude
  - Type d'établissement (enum)
  - Label (admin seulement)
  - Visité (admin seulement)

### Logique d'édition JavaScript

```javascript
// Pour les évaluations
export function editEvaluation(idEval) {
    const displayElement = document.getElementById('evaluation-' + idEval + '-display');
    const editElement = document.getElementById('evaluation-' + idEval + '-edit');
    
    if (displayElement && editElement) {
        displayElement.style.display = 'none';
        editElement.style.display = 'block';
    }
}
```

### Droits d'édition

Toutes les entités suivent la même logique de droits :
- Seuls le créateur ou un admin peuvent modifier/supprimer
- Les admins ont accès à des champs supplémentaires
- Vérification côté serveur ET côté client

## Routes Flask

### Routes CRUD

#### Évaluations
```python
@main_bp.route("/evaluation/<int:id_eval>", methods=["GET"])
def afficher_evaluation_unique(id_eval):
    # Affichage avec initialisation du formulaire
    
@main_bp.route("/modifier_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def modifier_evaluation(id_eval):
    # Vérification des droits + mise à jour
    
@main_bp.route("/valider_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def valider_evaluation(id_eval):
    # Admin seulement - changement de statut
    
@main_bp.route("/supprimer_evaluation/<int:id_eval>", methods=["POST"])
@login_required
def supprimer_evaluation(id_eval):
    # Suppression avec vérification des droits
```

#### Flans
Structure similaire mais avec :
- Routes préfixées `/flan/` et `/modifier_flan/`
- Logique de mise à jour des attributs spécifiques
- Calcul de la moyenne des évaluations

#### Établissements
Structure similaire mais avec :
- Routes préfixées `/etablissement/` et `/modifier_etablissement/`
- Gestion des coordonnées géographiques
- Champs admin (label, visite)

### Logique métier spécifique

#### Évaluations
```python
def mise_a_jour_evaluation(form, id_flan, id_user, is_admin=False):
    # Conversion des notes en float
    visuel = float(str(form.visuel.data).replace(",", "."))
    texture = float(str(form.texture.data).replace(",", "."))
    pate = float(str(form.pate.data).replace(",", "."))
    gout = float(str(form.gout.data).replace(",", "."))
    
    # Création/mise à jour de l'évaluation
    evaluation = Evaluation.query.filter_by(id_flan=id_flan, id_user=id_user).first()
    
    if evaluation:
        # Mise à jour
    else:
        # Création
    
    # Calcul de la moyenne
    moyenne = (visuel + texture + pate + gout) / 4
```

#### Flans
```python
# Dans le modèle Flan
def get_moyenne_evaluations(self):
    if self.evaluations:
        total = sum(e.get_moyenne() for e in self.evaluations)
        return total / len(self.evaluations)
    return None
```

## JavaScript

### Gestion des événements

#### Évaluations
- `editEvaluation(idEval)` : Bascule vers le mode édition
- `cancelEditEval(idEval)` : Annule l'édition
- Écouteurs d'événements sur les boutons d'action

#### Flans
- Fonctions similaires mais adaptées aux champs spécifiques
- Gestion des sélecteurs pour les enums (pâte, saveur, texture)

#### Établissements
- Gestion complexe avec :
  - Autocomplete pour la recherche
  - Géolocalisation
  - Intégration avec la carte Google Maps
  - Champs cachés pour les coordonnées

### Intégration avec les macros Jinja2

Toutes les entités utilisent le système de macros mais avec des paramètres spécifiques :

```jinja2
{{ afficher_boutons_actions(
    evaluation, 
    current_user, 
    'id_eval', 
    'main.modifier_evaluation', 
    'main.supprimer_evaluation', 
    'main.valider_evaluation',
    'evaluation', 
    current_page, 
    delete_form, 
    validate_form
) }}
```

## Différences clés

### Hiérarchie des données

```
Établissement
└── Flan
    └── Évaluation
```

- Les évaluations sont liées à un flan spécifique
- Les flans sont liés à un établissement spécifique
- Les établissements sont indépendants

### Workflow utilisateur

#### Évaluations
1. L'utilisateur doit être authentifié
2. Peut seulement évaluer un flan existant
3. Une seule évaluation par utilisateur par flan
4. Affichage d'un message si évaluation déjà existante

#### Flans
1. L'utilisateur doit être authentifié
2. Peut proposer un flan pour un établissement existant
3. Plusieurs flans possibles par établissement
4. Formulaire accessible depuis la page de l'établissement

#### Établissements
1. L'utilisateur doit être authentifié
2. Peut proposer un nouvel établissement
3. Processus de création plus complexe avec :
   - Recherche Google Places
   - Sélection sur carte
   - Validation des coordonnées

### Validation et statut

- **Évaluations** : 
  - Statut VALIDE/INVALIDE
  - Validation par admin
  - Badge de validation visible

- **Flans** :
  - Statut VALIDE/INVALIDE
  - Validation par admin
  - Impact sur l'affichage dans les recherches

- **Établissements** :
  - Statut VALIDE/INVALIDE
  - Validation par admin
  - Champs supplémentaires :
    - Label (❤️)
    - Visité

### Affichage des moyennes

- **Évaluations** : 
  - Moyenne des 4 critères (visuel, pâte, texture, goût)
  - Calcul côté template : `(gout + texture + visuel + pate) / 4`

- **Flans** :
  - Moyenne de toutes ses évaluations
  - Méthode `get_moyenne_evaluations()`
  - Impact sur le classement

- **Établissements** :
  - Nombre de flans proposés
  - Pas de système de notation direct
  - Affichage du compte des flans

### Complexité des formulaires

| Entité | Champs | Complexité |
|---------|--------|------------|
| Évaluation | 4 notes + description | Simple |
| Flan | 5 champs (nom, prix, 3 enums) | Moyenne |
| Établissement | 8+ champs (coordonnées, adresse, options admin) | Complexe |

## Conclusion

Bien que les trois entités partagent une architecture commune (affichage, édition, validation), elles présentent des différences significatives :

1. **Les évaluations** ont une logique simple et sont étroitement liées aux flans
2. **Les flans** servent de pont entre établissements et évaluations
3. **Les établissements** ont la gestion la plus complexe avec des fonctionnalités géographiques et administratives

Cette architecture reflète la hiérarchie naturelle des données : un utilisateur évalue un flan dans un établissement, créant ainsi une relation à trois niveaux qui structure toute l'application.

---

*Document généré le 13/01/2026 - Analyse basée sur le code source de PlanFlan v2*