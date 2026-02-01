# Optimisations CI/CD - Cache et Skip Intelligent

## 📋 Vue d'ensemble

Ce document décrit les optimisations apportées aux workflows CI/CD pour améliorer les performances et réduire les coûts d'exécution.

## 🎯 Objectifs Atteints

### 1. Cache des Dépendances
- ✅ **Cache pip Python** : Les dépendances Python sont maintenant mises en cache entre les exécutions
- ✅ **Cache npm Node.js** : Les dépendances JavaScript sont mises en cache
- ✅ **Cache Docker layers** : Les layers Docker sont réutilisés pour accélérer les builds

### 2. Skip Intelligent des Tests
- ✅ **Vérification via API GitHub** : Lorsqu'un commit de `dev` est mergé sur `main`, le workflow vérifie si les tests ont déjà réussi sur `dev`
- ✅ **Skip conditionnel** : Si tous les checks ont réussi sur `dev`, la CI est skippée sur `main`
- ✅ **Pre-deploy optimisé** : Les vérifications de syntaxe sont skippées si CI a déjà réussi

### 3. Corrections des Incohérences
- ✅ **Suppression de `--no-cache-dir`** : Contradictoire avec le cache pip d'Actions
- ✅ **Standardisation requirements-dev.txt** : Hérite maintenant de requirements.txt pour éviter les duplications
- ✅ **Utilisation de build-push-action** : Remplace les commandes Docker manuelles pour un meilleur cache

## 🔧 Changements Techniques

### CI Workflow (`.github/workflows/ci.yml`)

#### 1. Check Commit Amélioré
```yaml
# Avant : Comparaison de hash de contenu
# Après : Vérification du statut CI via l'API GitHub

- Vérifie si le commit existe sur dev
- Interroge l'API GitHub pour le statut des workflows
- Skip si tous les checks sont ✅ success
```

#### 2. Cache Pip
```yaml
# Avant
cache: 'pip'
cache-dependency-path: 'requirements.txt'
pip install --no-cache-dir -r requirements.txt  # ❌ Contradictoire

# Après
cache: 'pip'
cache-dependency-path: |
  requirements.txt
  requirements-dev.txt
pip install -r requirements.txt  # ✅ Utilise le cache
```

#### 3. Cache Docker avec Buildx
```yaml
# Avant : docker build basique
docker build -t image:tag .

# Après : build-push-action avec cache
- uses: docker/build-push-action@v5
  with:
    cache-from: type=local,src=/tmp/.buildx-cache
    cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

**Gain estimé** : 30-60% de réduction du temps de build Docker

### CD Workflow (`.github/workflows/cd.yml`)

#### 1. Cache Pip Amélioré
```yaml
cache-dependency-path: |
  requirements.txt
  requirements-dev.txt
```

### Pre-Deploy Checks (`.github/workflows/pre-deploy-checks.yml`)

#### 1. Nouveau Job de Vérification CI
```yaml
jobs:
  check-ci-status:
    # Vérifie si CI a déjà réussi pour ce commit
    
  pre-deploy-checks:
    needs: check-ci-status
    # Skip certaines étapes si CI a réussi
```

#### 2. Cache Node.js Ajouté
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: 'package-lock.json'
```

#### 3. Étapes Conditionnelles
```yaml
- name: Check Python syntax
  if: needs.check-ci-status.outputs.ci_passed != 'true'
  # Skip si CI a déjà validé la syntaxe
```

### Requirements-dev.txt

#### Avant
```txt
# Duplications avec requirements.txt
pytest==9.0.2
coverage
black
```

#### Après
```txt
# Inclure les dépendances de production
-r requirements.txt

# Seulement les dépendances dev uniques
pytest-cov==7.0.0
pytest-xdist==3.6.1
```

**Avantage** : Maintenance simplifiée, pas de versions conflictuelles

## 📊 Gains de Performance Estimés

| Workflow | Avant | Après | Gain |
|----------|-------|-------|------|
| CI sur dev (première fois) | 8-10 min | 8-10 min | 0% |
| CI sur dev (avec cache) | 8-10 min | 5-7 min | ~35% |
| CI sur main (fast-forward) | 8-10 min | ~30s (skip) | ~95% |
| Pre-deploy (après CI) | 6-8 min | 3-4 min | ~45% |
| Docker build (avec cache) | 4-6 min | 2-3 min | ~50% |

**Économies estimées** :
- **Par merge dev→main** : ~15 minutes
- **Par jour** (avec 3-5 merges) : ~45-75 minutes
- **Par mois** : ~20-30 heures de compute

## 🚀 Workflow de Développement Optimisé

### Scénario 1 : Développement sur Dev
```bash
1. git checkout dev
2. # ... développement ...
3. git commit -m "Feature X"
4. git push origin dev

→ CI s'exécute normalement
→ Cache pip/npm/docker utilisé si disponible
→ Temps : 5-7 min (avec cache)
```

### Scénario 2 : Merge Dev → Main (Fast-forward)
```bash
1. git checkout main
2. git merge dev --ff-only
3. git push origin main

→ CI vérifie le statut du commit sur dev
→ Trouve que tous les checks ont réussi ✅
→ Skip CI sur main
→ Pre-deploy checks optimisés
→ Temps : ~30s + 3-4 min = ~5 min total
```

### Scénario 3 : Hotfix Direct sur Main
```bash
1. git checkout main
2. # ... hotfix ...
3. git commit -m "Hotfix Y"
4. git push origin main

→ Commit n'existe pas sur dev
→ CI s'exécute normalement
→ Cache utilisé
→ Temps : 5-7 min
```

## 🔍 Vérification du Skip

Pour vérifier si un commit a été skippé :

```bash
# Via GitHub CLI
gh run list --commit $(git rev-parse HEAD) --json conclusion

# Via l'interface GitHub
# Actions → CI Pipeline → Check commit status
```

## ⚙️ Configuration Requise

### Secrets GitHub (inchangés)
- `GITHUB_TOKEN` : Fourni automatiquement par GitHub Actions
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `PRODUCTION_SERVER`
- `PRODUCTION_USER`
- `SSH_PRIVATE_KEY`

### Permissions du Token
Le `GITHUB_TOKEN` doit avoir les permissions :
- `checks: read` (pour lire les statuts des workflows)
- `statuses: read` (pour lire les statuts des commits)

**Note** : Ces permissions sont accordées par défaut aux workflows GitHub Actions.

## 🐛 Dépannage

### Le cache ne fonctionne pas
```yaml
# Vérifier que cache-dependency-path pointe vers les bons fichiers
cache-dependency-path: |
  requirements.txt
  requirements-dev.txt

# Forcer la regénération du cache (temporaire)
- name: Clear cache
  run: rm -rf ~/.cache/pip
```

### Le skip ne fonctionne pas
```bash
# Vérifier que le commit existe sur dev
git branch -r --contains <commit-sha>

# Vérifier le statut CI via l'API
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/commits/SHA/check-runs
```

### Docker cache trop volumineux
```yaml
# Limiter la taille du cache (déjà configuré)
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max

# Le mode 'max' garde tous les layers intermédiaires
# Alternative : mode=min (seulement l'image finale)
```

## 📝 Maintenance

### Nettoyage Périodique
GitHub Actions nettoie automatiquement les caches après 7 jours d'inactivité.

### Mise à Jour des Versions d'Actions
Les versions d'actions sont maintenant standardisées :
- `actions/checkout@v4`
- `actions/setup-python@v4`
- `actions/setup-node@v4`
- `actions/cache@v3`
- `docker/setup-buildx-action@v3`
- `docker/login-action@v3`
- `docker/build-push-action@v5`

## 🎓 Ressources

- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Docker Buildx Cache](https://docs.docker.com/build/cache/)
- [GitHub Status API](https://docs.github.com/en/rest/commits/statuses)
- [Check Runs API](https://docs.github.com/en/rest/checks/runs)

## 🔄 Prochaines Étapes (Optionnel)

### Optimisations Supplémentaires Possibles
1. **Cache distribué** : Utiliser un registry cache pour Docker (GitHub Container Registry)
2. **Matrix builds** : Paralléliser les tests par catégorie
3. **Artifacts partagés** : Partager les builds entre jobs
4. **Self-hosted runners** : Pour des builds encore plus rapides (si budget disponible)

### Monitoring
1. **GitHub Insights** : Analyser les temps d'exécution des workflows
2. **Cost tracking** : Suivre les minutes consommées
3. **Cache hit ratio** : Mesurer l'efficacité du cache

---

**Dernière mise à jour** : 2026-02-01
**Version** : 1.0
**Auteur** : Optimisation CI/CD
