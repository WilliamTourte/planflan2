# 📊 Configuration de Coverage et Intégration CI/CD

*Dernière mise à jour : 6 janvier 2026*

## Table des matières

- [📊 Configuration de Coverage et Intégration CI/CD](#📊-configuration-de-coverage-et-intégration-cicd)
- [Table des matières](#table-des-matières)
- [🎯 Introduction](#🎯-introduction)
- [🔧 Configuration Actuelle](#🔧-configuration-actuelle)
  - [Fichiers de configuration modifiés](#fichiers-de-configuration-modifiés)
  - [Améliorations clés](#améliorations-clés)
- [🚀 Utilisation des Rapports de Coverage](#🚀-utilisation-des-rapports-de-coverage)
  - [Commandes Makefile](#commandes-makefile)
  - [Script d'assistance](#script-dassistance)
  - [Génération manuelle](#génération-manuelle)
- [🤖 Intégration CI/CD](#🤖-intégration-cicd)
  - [Configuration GitHub Actions](#configuration-github-actions)
  - [Configuration GitLab CI](#configuration-gitlab-ci)
  - [Configuration Jenkins](#configuration-jenkins)
  - [Configuration CircleCI](#configuration-circleci)
- [📈 Interprétation des Rapports](#📈-interprétation-des-rapports)
  - [Rapport HTML](#rapport-html)
  - [Rapport XML (Cobertura)](#rapport-xml-cobertura)
  - [Rapport Terminal](#rapport-terminal)
- [⚠️ Dépannage](#⚠️-dépannage)
  - [Problèmes courants](#problèmes-courants)
  - [Solutions](#solutions)
- [🔄 Maintenance et Bonnes Pratiques](#🔄-maintenance-et-bonnes-pratiques)
- [📚 Références](#📚-références)

## 🎯 Introduction

Ce document décrit la configuration améliorée des rapports de coverage pour le projet PlanFlan, incluant la génération automatique de rapports HTML et XML pour le développement local et l'intégration continue (CI/CD).

## 🔧 Configuration Actuelle

### Fichiers de configuration modifiés

1. **`pytest.ini`** - Configuration principale de pytest et coverage
2. **`Makefile`** - Ajout de cibles pour la génération de rapports
3. **`.gitignore`** - Gestion des fichiers de coverage
4. **`scripts/ensure_coverage.sh`** - Script d'assistance pour la génération robuste

### Améliorations clés

#### 1. Génération automatique des rapports

- **HTML** : Toujours généré pour le développement local
- **XML** : Toujours généré pour l'intégration CI/CD (format Cobertura)
- **Terminal** : Rapport textuel par défaut

#### 2. Configuration pytest.ini

```ini
# Rapport HTML - toujours généré
html:
    directory = htmlcov
    always = True  # ← Nouvelle option

# Rapport XML pour l'intégration CI
xml:
    report_file = coverage.xml
    always = True  # ← Nouvelle option

# Rapport terminal par défaut
term:
    report = True
    skip_covered = False
```

#### 3. Nouvelles cibles Makefile

- `test-full-coverage` : Exécute tous les tests avec tous les rapports
- `test-ci` : Optimisé pour les pipelines CI/CD
- `coverage-html` : Génère uniquement le rapport HTML
- `coverage-check-xml` : Vérifie la présence du fichier XML pour CI
- `coverage-clean` : Nettoie les anciens rapports

## 🚀 Utilisation des Rapports de Coverage

### Commandes Makefile

#### Pour le développement quotidien

```bash
# Exécuter tous les tests avec coverage complet
make test-full-coverage

# Voir le rapport textuel
make coverage-report

# Nettoyer et regénérer
make coverage-clean coverage-html
```

#### Pour CI/CD

```bash
# Exécuter les tests optimisés pour CI
make test-ci

# Vérifier que le fichier XML existe
make coverage-check-xml
```

### Script d'assistance

Le script `scripts/ensure_coverage.sh` offre une solution robuste :

```bash
# Exécuter tous les tests avec coverage
./scripts/ensure_coverage.sh

# Exécuter des tests spécifiques
./scripts/ensure_coverage.sh "python -m pytest tests/test_main.py"
```

### Génération manuelle

```bash
# Générer uniquement le rapport HTML
coverage html

# Générer uniquement le rapport XML
coverage xml

# Générer un rapport textuel détaillé
coverage report --show-missing
```

## 🤖 Intégration CI/CD

### Configuration GitHub Actions

```yaml
name: CI with Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests with coverage
      run: make test-ci
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: coverage.xml
        flags: unittests
        name: codecov-planflan
        fail_ci_if_error: true
```

### Configuration GitLab CI

```yaml
stages:
  - test
  - coverage

test_job:
  stage: test
  script:
    - pip install -r requirements.txt
    - make test-ci
  artifacts:
    paths:
      - coverage.xml
    expire_in: 1 week

coverage_job:
  stage: coverage
  script:
    - echo "Coverage report generated"
  needs: [test_job]
  dependencies:
    - test_job
```

### Configuration Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install') {
            steps {
                sh 'pip install -r requirements-dev.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh 'make test-ci'
            }
        }
        
        stage('Coverage') {
            steps {
                // Publish coverage using Cobertura plugin
                publishCoverage adaptors: [coberturaAdapter('coverage.xml')]
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
        }
    }
}
```

### Configuration CircleCI

```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.13
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      - run:
          name: Run tests with coverage
          command: make test-ci
      - store_artifacts:
          path: coverage.xml
      - store_test_results:
          path: test-results

workflows:
  test-and-coverage:
    jobs:
      - test
```

## 📈 Interprétation des Rapports

### Rapport HTML

- **Localisation** : `htmlcov/index.html`
- **Format** : Interface web interactive
- **Fonctionnalités** :
  - Navigation par fichiers
  - Filtrage des fichiers couverts
  - Visualisation des lignes manquantes
  - Statistiques détaillées

**Accès** :
```bash
# Ouvrir dans le navigateur
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # Mac
start htmlcov/index.html     # Windows
```

### Rapport XML (Cobertura)

- **Localisation** : `coverage.xml`
- **Format** : XML standard Cobertura
- **Utilisation** : Intégration CI/CD
- **Structure** :
  ```xml
  <coverage version="7.13.0" line-rate="0.80" branch-rate="0.63">
    <sources><source>/chemin/du/projet/app</source></sources>
    <packages>
      <package name="." line-rate="0.85">
        <classes>
          <class name="main.py" line-rate="0.83">
            <lines><line number="42" hits="1"/></lines>
          </class>
        </classes>
      </package>
    </packages>
  </coverage>
  ```

### Rapport Terminal

Exemple de sortie :
```
Name                              Stmts   Miss  Cover   Missing
----------------------------------------------------------------
app/config.py                        16      0   100%
app/forms.py                        163     25    85%   45-48, 82-85
app/models.py                       150      8    95%   122-125
app/routes/main.py                  416     72    83%   105-112, 201-210
----------------------------------------------------------------
TOTAL                              3714    689    81%
```

## ⚠️ Dépannage

### Problèmes courants

1. **Pas de fichier XML généré**
   - Solution : Vérifier que `--cov-report=xml` est utilisé
   - Solution : Exécuter `make coverage-check-xml`

2. **Coverage à 0%**
   - Solution : Vérifier que les tests exécutent bien le code
   - Solution : Nettoyer avec `make coverage-clean` et relancer

3. **Fichiers manquants dans le rapport**
   - Solution : Vérifier la configuration `source` dans pytest.ini
   - Solution : Vérifier les exclusions dans `omit`

4. **Avertissements "No data collected"**
   - Solution : S'assurer que le code est importé correctement
   - Solution : Vérifier les chemins d'importation

### Solutions

```bash
# Réinitialiser complètement la configuration
make coverage-clean
rm -f .coverage

# Relancer avec une configuration propre
python -m pytest tests/test_app.py --cov=app --cov-report=xml --cov-report=html -v

# Vérifier la configuration
coverage debug config
coverage debug sys
```

## 🔄 Maintenance et Bonnes Pratiques

1. **Exécuter régulièrement** : `make test-full-coverage` pour maintenir la qualité
2. **Vérifier les régressions** : Comparer les rapports avant/après les modifications
3. **Documenter les exclusions** : Justifier les fichiers omis dans pytest.ini
4. **Mettre à jour les cibles** : Ajouter de nouvelles fonctionnalités aux tests
5. **Surveiller la tendance** : Le coverage devrait augmenter ou rester stable

**Seuils recommandés** :
- 🟢 Excellent : > 90%
- 🟡 Bon : 80-90%
- 🟠 Acceptable : 70-80%
- ❌ À améliorer : < 70%

## 📚 Références

- [Documentation officielle coverage.py](https://coverage.readthedocs.io/)
- [Format Cobertura XML](https://github.com/cobertura/cobertura/wiki/XML-Report-Format)
- [Intégration GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests)
- [Intégration GitLab CI](https://docs.gitlab.com/ee/ci/)
- [Plugin Cobertura pour Jenkins](https://plugins.jenkins.io/cobertura/)

---

*Document généré automatiquement par Mistral Vibe - 6 janvier 2026*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*