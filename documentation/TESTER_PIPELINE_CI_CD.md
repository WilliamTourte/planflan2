# Guide pour Tester la Pipeline CI/CD

Ce guide vous explique comment tester progressivement votre pipeline CI/CD sans Pylint.

## 🎯 Objectif

Tester la pipeline CI/CD étape par étape pour s'assurer que tout fonctionne avant d'ajouter Pylint plus tard.

## 🚀 Étapes pour Tester la Pipeline

### 1. Préparation Locale

Avant de pousser vers GitHub, vérifiez que tout fonctionne localement :

```bash
# 1. Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Exécuter les tests unitaires
python -m pytest tests/ -m "unitary" -v --tb=short

# 3. Exécuter les tests critiques
python -m pytest tests/ -m "critical" -v --tb=short

# 4. Formater le code avec Black
black app/

# 5. Tester les hooks pre-commit
pre-commit run --all-files
```

### 2. Premier Test CI (Branche de Test)

Créez une branche de test pour vérifier que la pipeline CI fonctionne :

```bash
# Créer une branche de test
git checkout -b test/ci-pipeline

# Faire un petit changement (ex: ajouter un commentaire)
echo "# Test CI Pipeline" >> README.md

# Commiter et pousser
git add README.md
git commit -m "Test: Vérification pipeline CI"
git push origin test/ci-pipeline
```

### 3. Surveillance de la Pipeline

1. Allez sur GitHub dans votre dépôt
2. Cliquez sur l'onglet "Actions"
3. Sélectionnez le workflow "CI Pipeline"
4. Cliquez sur l'exécution en cours

### 4. Vérification des Étapes

La pipeline devrait exécuter :

- ✅ Checkout du code
- ✅ Configuration Python
- ✅ Installation des dépendances
- ✅ Tests unitaires
- ✅ Tests critiques
- ✅ Génération du rapport de couverture
- ✅ Construction Docker
- ✅ Tests du conteneur Docker

### 5. Correction des Problèmes

Si la pipeline échoue :

```bash
# Voir les logs détaillés dans l'interface GitHub
# Identifier l'étape qui a échoué

# Corriger le problème localement
# Exemple si les tests échouent :
python -m pytest tests/test_echoue.py -v

# Recommiter et repousser
git add .
git commit -m "Fix: Correction du test échoué"
git push origin test/ci-pipeline
```

## 📋 Checklist de Vérification

- [ ] Les tests unitaires passent localement
- [ ] Les tests critiques passent localement
- [ ] Black formate correctement le code
- [ ] Les hooks pre-commit passent
- [ ] La pipeline CI se déclenche sur push
- [ ] Toutes les étapes de la CI passent
- [ ] Le rapport de couverture est généré
- [ ] L'image Docker est construite avec succès
- [ ] Le conteneur Docker démarre correctement

## 🛠 Dépannage Courant

### Problème 1: La pipeline ne se déclenche pas

**Causes possibles** :
- Le fichier modifié n'est pas dans les paths surveillés
- Problème de permissions GitHub Actions

**Solution** :
```yaml
# Dans .github/workflows/ci.yml, vérifiez la section "paths"
paths:
  - 'Dockerfile'
  - 'docker-compose.yml'
  - 'entrypoint.sh'
  - 'app/**'
  - 'tests/**'
```

### Problème 2: Échec de l'installation des dépendances

**Solution** :
```bash
# Tester localement dans un environnement propre
python -m venv test_venv
source test_venv/bin/activate  # Linux/Mac
# ou test_venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Problème 3: Échec des tests

**Solution** :
```bash
# Exécuter les tests localement avec le même marqueur
python -m pytest tests/ -m "unitary" -v --tb=short

# Voir les tests disponibles
python -m pytest tests/ --collect-only -q
```

### Problème 4: Échec de la construction Docker

**Solution** :
```bash
# Tester la construction localement
docker build -t planflan.backend:test .

# Vérifier les logs
docker run --name test-container -d planflan.backend:test
docker logs test-container
```

## 🎓 Bonnes Pratiques pour les Tests

### 1. Commencez petit
- Faites des changements mineurs pour tester
- Évitez de tout changer en même temps

### 2. Testez les différentes branches
- Testez sur `dev` puis sur `main`
- Vérifiez que les deux branches déclenchent la pipeline

### 3. Surveillez les performances
- Notez le temps d'exécution de chaque étape
- Identifiez les goulots d'étranglement

### 4. Documentez les problèmes
- Créez des issues GitHub pour les problèmes trouvés
- Notez les solutions dans la documentation

## 📊 Métriques à Surveiller

| Métrique | Valeur Cible | Comment Mesurer |
|----------|-------------|------------------|
| Temps d'exécution CI | < 10 min | Chronométrez dans l'interface GitHub |
| Taux de succès | > 90% | Statistiques GitHub Actions |
| Couverture de code | > 80% | Rapport coverage.xml |
| Temps de construction Docker | < 5 min | Étape "Build Docker image" |

## 🔄 Prochaines Étapes Après Validation

Une fois que la pipeline fonctionne sans Pylint :

1. **Ajouter Pylint progressivement** :
   ```bash
   # D'abord en mode avertissement seulement
   pylint app/ --rcfile=.pylintrc --exit-zero
   
   # Puis en mode bloquant
   pylint app/ --rcfile=.pylintrc
   ```

2. **Configurer les notifications** :
   - Ajouter des notifications Slack/Email
   - Configurer les alertes pour les échecs

3. **Optimiser la pipeline** :
   - Ajouter du caching pour les dépendances
   - Paralleliser les tests
   - Utiliser des matrices de test

4. **Documenter les processus** :
   - Créer un guide pour les nouveaux contributeurs
   - Documenter les procédures de déploiement

## 📚 Commandes Utiles pour le Dépannage

```bash
# Voir l'état des workflows
gh workflow list

# Voir les runs d'un workflow
gh run list

# Voir les logs d'un run spécifique
gh run view <run-id> --log

# Redémarrer un workflow échoué
gh run rerun <run-id>

# Annuler un workflow en cours
gh run cancel <run-id>
```

## 🎉 Validation Finale

Une fois que tout fonctionne :

1. **Fusionnez votre branche de test** :
   ```bash
   git checkout dev
   git merge test/ci-pipeline
   git push origin dev
   ```

2. **Testez sur la branche main** :
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

3. **Célébrez !** 🎉
   - Votre pipeline CI/CD est opérationnelle
   - Vous pouvez maintenant ajouter Pylint en toute confiance

## 📅 Plan de Test Recommandé

| Jour | Action | Objectif |
|------|--------|----------|
| 1 | Test sur branche de test | Valider le fonctionnement de base |
| 2 | Test sur dev | Vérifier l'intégration avec la branche de développement |
| 3 | Correction des problèmes | Résoudre les échecs identifiés |
| 4 | Test sur main | Valider le déploiement (sans déploiement réel) |
| 5 | Documentation | Documenter les processus et procédures |
| 6 | Formation équipe | Former les autres développeurs |
| 7 | Ajout Pylint | Réactiver Pylint progressivement |

---

*Dernière mise à jour : 14 janvier 2026*
*Version : 1.0*