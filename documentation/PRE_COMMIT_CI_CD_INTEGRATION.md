# Intégration Pre-commit et CI/CD pour PlanFlan

Ce document explique comment les hooks pre-commit et la pipeline CI/CD travaillent ensemble pour garantir la qualité du code.

## 🎯 Objectifs de l'Intégration

1. **Cohérence** : Expérience uniforme entre développement local et CI/CD
2. **Détection précoce** : Attraper les erreurs avant le commit
3. **Efficacité** : Équilibre entre vérifications rapides locales et complètes en CI
4. **Qualité** : Maintenir un haut niveau de qualité de code

## 🔧 Configuration Actuelle

### Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
# Formatage de code
- Black: Vérifie TOUS les fichiers Python dans app/ (anciennement forms.py uniquement)

# Analyse statique
- Pylint: Vérifie TOUS les fichiers Python dans app/ avec .pylintrc (anciennement forms.py avec désactivations)

# Tests
- pytest-smoke: Tests rapides marqués @pytest.mark.smoke
- pytest-critical: Tests critiques marqués @pytest.mark.critical

# Avertissements
- ci-cd-warning: Rappel des différences entre local et CI
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# Dans .github/workflows/ci.yml et pre-deploy-checks.yml
- Pylint: Même configuration que pre-commit, mais sur tout le code
- Tests: Tous les tests + couverture de code (80% minimum)
- Sécurité: Bandit et Safety
- Docker: Construction et tests des images
```

## 🔄 Changements Apportés

### Avant (Conflits Potentiels)

| Outil | Pre-commit | CI/CD | Problème |
|-------|-----------|-------|----------|
| Black | `app/forms.py` uniquement | Non utilisé | Incohérence |
| Pylint | `app/forms.py` avec désactivations | Tout `app/` sans désactivations | Échecs inattendus |
| Tests | Tests smoke uniquement | Tous les tests | Faux sentiment de sécurité |

### Après (Alignement Complet)

| Outil | Pre-commit | CI/CD | Bénéfice |
|-------|-----------|-------|----------|
| Black | Tout `app/*.py` | Non utilisé | Cohérence |
| Pylint | Tout `app/*.py` avec `.pylintrc` | Tout `app/*.py` avec `.pylintrc` | Même règles |
| Tests | Smoke + Critiques | Tous + Couverture | Détection progressive |

## ✅ Avantages de l'Alignement

### 1. Expérience Développeur Améliorée
- **Prévisibilité** : Ce qui passe en local passe en CI
- **Rapidité** : Feedback immédiat avant le commit
- **Confiance** : Moins de surprises lors des pushes

### 2. Qualité de Code Renforcée
- **Couverture étendue** : Tous les fichiers sont vérifiés, pas seulement `forms.py`
- **Règles uniformes** : Même niveau de qualité partout
- **Détection précoce** : Les problèmes sont attrapés plus tôt

### 3. Efficacité du Workflow
- **Moins de cycles CI** : Les erreurs sont corrigées avant le push
- **Reviews plus rapides** : Le code arrive déjà validé
- **Déploiements plus fiables** : La CI/CD a moins de surprises

## 🚀 Workflow de Développement Recommandé

```
1. Créer une feature branch
   git checkout -b feature/ma-nouvelle-fonctionnalite

2. Développer le code
   # ... modifications ...

3. Exécuter les hooks pre-commit
   git add .
   git commit -m "Ajout de la nouvelle fonctionnalité"
   # → Black, Pylint, tests smoke et critiques s'exécutent

4. Corriger les problèmes locaux
   # ... corrections ...
   git add .
   git commit --amend

5. Pousser vers GitHub
   git push origin feature/ma-nouvelle-fonctionnalite

6. Créer une Pull Request
   # → CI/CD s'exécute automatiquement
   # → Vérifications pré-déploiement complets

7. Revue et fusion
   # → Après approbation, fusion vers dev
   # → Puis vers main pour déploiement automatique
```

## 🛠 Configuration Technique

### Fichiers Modifiés

1. **`.pre-commit-config.yaml`** :
   - Étendu Black à tous les fichiers Python
   - Étendu Pylint à tous les fichiers Python
   - Enlevé les désactivations spécifiques de Pylint
   - Ajouté tests critiques
   - Ajouté avertissement CI/CD

2. **`.pylintrc`** : (inchangé, utilisé par les deux)
   - Configuration centrale pour le linting
   - Appliqué uniformément

### Commandes Utiles

```bash
# Installer/maj les hooks pre-commit
pre-commit install
pre-commit autoupdate

# Exécuter manuellement tous les hooks
pre-commit run --all-files

# Exécuter un hook spécifique
pre-commit run pylint --all-files
pre-commit run black --all-files

# Désactiver temporairement les hooks
SKIP=black,pylint git commit -m "Message"
```

## ⚠️ Différences Restantes (Volontaires)

| Aspect | Pre-commit | CI/CD | Raison |
|--------|-----------|-------|--------|
| **Portée des tests** | Smoke + Critiques | Tous les tests | Performance locale |
| **Couverture** | Non vérifiée | 80% minimum | Rapidité locale |
| **Sécurité** | Non exécutée | Bandit + Safety | Dépendances lourdes |
| **Docker** | Non testé | Construction complète | Environnement requis |

## 📊 Comparaison des Temps d'Exécution

| Tâche | Pre-commit (local) | CI/CD (GitHub) |
|-------|-------------------|----------------|
| Black | ~2-5s | N/A |
| Pylint | ~10-30s | ~15-40s |
| Tests | ~30-60s | ~2-5min |
| Sécurité | N/A | ~1-2min |
| Docker | N/A | ~3-8min |
| **Total** | **~45-90s** | **~6-15min** |

## 🎓 Bonnes Pratiques

### Pour les Développeurs

1. **Exécutez les hooks avant de pousser** :
   ```bash
   pre-commit run --all-files
   ```

2. **Corrigez les problèmes de formatage** :
   ```bash
   black app/
   ```

3. **Testez localement avant la PR** :
   ```bash
   make test-quick  # Tests rapides
   make test-all    # Tests complets
   ```

### Pour les Mainteneurs

1. **Mettez à jour les hooks régulièrement** :
   ```bash
   pre-commit autoupdate
   ```

2. **Ajoutez des tests smoke** :
   ```python
   @pytest.mark.smoke
   def test_fonctionnalite_critique():
       # Test rapide et essentiel
   ```

3. **Maintenez `.pylintrc` à jour** :
   - Ajoutez des exceptions si nécessaire
   - Documentez les règles

## 🔄 Migration depuis l'Ancienne Configuration

### Changements pour les Développeurs

1. **Plus de fichiers vérifiés** :
   - Avant : Seulement `app/forms.py`
   - Maintenant : Tous les fichiers Python dans `app/`

2. **Règles Pylint plus strictes** :
   - Les codes `C0114,C0115,C0116,W0613` ne sont plus désactivés
   - Vous devrez peut-être :
     - Ajouter des docstrings
     - Utiliser tous les arguments des fonctions
     - Renommer les variables selon les conventions

3. **Plus de tests locaux** :
   - Les tests critiques s'exécutent maintenant en pre-commit
   - Cela peut ralentir légèrement les commits (mais évite les échecs CI)

### Comment Migrer Votre Code

1. **Exécuter Black sur tout le code** :
   ```bash
   black app/
   ```

2. **Corriger les problèmes Pylint** :
   ```bash
   pylint app/ --rcfile=.pylintrc
   ```

3. **Ajouter les docstrings manquantes** :
   ```python
   def ma_fonction(param):
       """Description de la fonction.
       
       Args:
           param: Description du paramètre
           
       Returns:
           Description de la valeur de retour
       """
       # ... code ...
   ```

4. **Vérifier que tous les tests passent** :
   ```bash
   make test-all
   ```

## 🛡 Gestion des Exceptions

### Cas où vous devez contourner les hooks

```bash
# Désactiver temporairement un hook spécifique
SKIP=black git commit -m "WIP: Travail en cours sur le formatage"

# Désactiver tous les hooks
git commit --no-verify -m "Message"
```

⚠️ **À utiliser avec parcimonie** - Cela contourne les vérifications de qualité !

### Quand contourner les hooks

- Travail en cours (WIP) non finalisé
- Fichiers générés automatiquement
- Urgence critique (mais corrigez après !)

## 📈 Améliorations Futures

1. **Ajouter plus de tests smoke** :
   - Identifier les tests critiques
   - Les marquer avec `@pytest.mark.smoke`

2. **Optimiser les performances** :
   - Cache des dépendances
   - Exécution parallèle des tests

3. **Ajouter des hooks supplémentaires** :
   - `flake8` pour le style
   - `mypy` pour le typage
   - `isort` pour les imports

4. **Intégrer avec les IDE** :
   - Configuration VSCode/PyCharm pour exécuter les hooks automatiquement

## 📚 Références

- [Documentation Pre-commit](https://pre-commit.com/)
- [Documentation Black](https://black.readthedocs.io/)
- [Documentation Pylint](https://pylint.readthedocs.io/)
- [Documentation Pytest](https://docs.pytest.org/)

---

*Dernière mise à jour : 14 janvier 2026*
*Version : 1.0*