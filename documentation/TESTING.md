# Guide de test et déploiement pour PlanFlan

## 🧪 Automatisation des tests

Ce projet utilise pytest pour les tests automatisés avec les outils suivants :
- `pytest` : Framework de test
- `pytest-cov` : Génération de rapports de coverage
- `coverage` : Analyse de coverage

## 📁 Structure des tests

```
tests/
├── conftest.py          # Configuration des fixtures
├── test_auth.py         # Tests d'authentification
├── test_forms.py        # Tests de validation des formulaires
├── test_main.py         # Tests des routes principales
├── test_maps.py         # Tests des fonctionnalités de carte
├── test_outils.py       # Tests des fonctions utilitaires
├── test_scenarios.py    # Tests de scénarios
└── test_securite.py     # Tests de sécurité
```

## 🚀 Exécution des tests

### 1. Utilisation du script `run_tests.sh`

Le script `run_tests.sh` offre une interface simple pour exécuter les tests :

```bash
# Affiche l'aide
./run_tests.sh --help

# Exécute tous les tests
./run_tests.sh --all

# Exécute uniquement les tests de formulaires
./run_tests.sh --forms

# Exécute les tests avec coverage
./run_tests.sh --forms --coverage

# Exécute les tests avec rapport HTML de coverage
./run_tests.sh --forms --coverage --html
```

### 2. Utilisation du Makefile

Le Makefile offre des cibles prêtes à l'emploi :

```bash
# Affiche l'aide
make help

# Exécute tous les tests
make test

# Exécute uniquement les tests de formulaires
make test-forms

# Exécute les tests avec coverage
make test-coverage

# Exécute les tests avec rapport HTML de coverage
make test-html

# Nettoie les fichiers temporaires
make clean
```

### 3. Exécution directe avec pytest

```bash
# Exécute tous les tests
PYTHONPATH=. pytest tests/ -v

# Exécute un fichier de test spécifique
PYTHONPATH=. pytest tests/test_forms.py -v

# Exécute un test spécifique
PYTHONPATH=. pytest tests/test_forms.py::test_etabform_donnees_valides -v

# Exécute avec coverage
PYTHONPATH=. pytest tests/ --cov=app --cov-report=term

# Exécute avec rapport HTML de coverage
PYTHONPATH=. pytest tests/ --cov=app --cov-report=html --cov-report=term
```

## 📊 Rapports de coverage

Les rapports de coverage sont générés dans le répertoire `htmlcov/`. Après exécution avec l'option `--html`, ouvrez le fichier suivant dans votre navigateur :

```bash
# Ouvrir le rapport HTML (Linux)
xdg-open htmlcov/index.html

# Ouvrir le rapport HTML (Mac)
open htmlcov/index.html

# Ouvrir le rapport HTML (Windows)
start htmlcov/index.html
```

## 🎯 Intégration Continue (CI)

Pour intégrer ces tests dans un pipeline CI (GitHub Actions, GitLab CI, etc.), utilisez une commande comme :

```yaml
# Exemple pour GitHub Actions
- name: Install dependencies
  run: pip install -r requirements-dev.txt

- name: Run tests
  run: ./run_tests.sh --all --coverage

- name: Upload coverage report
  uses: actions/upload-artifact@v3
  with:
    name: coverage-report
    path: htmlcov/
```

## 📦 Déploiement

### Pré-requis pour le déploiement

1. Tous les tests doivent passer
2. Le coverage doit être supérieur à 80% (à ajuster selon vos besoins)
3. Aucune régression dans les tests existants

### Vérification pré-déploiement

```bash
# Exécuter tous les tests avec coverage
./run_tests.sh --all --coverage

# Vérifier que le coverage est suffisant
# (À implémenter selon vos critères)

# Nettoyer les fichiers temporaires
make clean
```

## 🔧 Configuration

- `.coveragerc` : Configuration du coverage
- `pytest.ini` : Configuration de pytest
- `requirements-dev.txt` : Dépendances de développement

## 💡 Bonnes pratiques

1. **Tests unitaires** : Testez chaque fonction et méthode individuellement
2. **Tests d'intégration** : Testez les interactions entre composants
3. **Tests de validation** : Testez les formulaires et les entrées utilisateur
4. **Tests de sécurité** : Testez les autorisations et les vulnérabilités
5. **Coverage** : Visez un coverage de 80% minimum pour le code critique

## 🎉 Résultats actuels

```
16 passed, 4 skipped, 4 warnings in 6.26s
Coverage: 38% (à améliorer progressivement)
```

Les 4 tests désactivés nécessitent soit des données en base de données, soit des validations spécifiques qui n'existent pas encore.

---

**Documentation mise à jour le 29/12/2024**