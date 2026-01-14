# Configuration de la Pipeline CI/CD pour PlanFlan

Ce guide explique comment configurer et utiliser la pipeline CI/CD pour le projet PlanFlan.

## 🎯 Objectifs de la Pipeline

La pipeline CI/CD automatise les processus suivants :

1. **Intégration Continue (CI)** :
   - Exécution automatique des tests après les changements Docker
   - Vérification de la qualité du code (linting, sécurité)
   - Génération de rapports de couverture
   - Construction et test des images Docker

2. **Livraison Continue (CD)** :
   - Déploiement automatique sur le serveur distant après fusion sur `main`
   - Vérifications pré-déploiement complètes
   - Tests post-déploiement
   - Mécanisme de rollback automatique en cas d'échec

3. **Vérifications Pré-déploiement** :
   - Analyse de sécurité
   - Vérification de la couverture de code
   - Validation des fichiers de configuration
   - Détection des secrets dans le code

## 🔧 Configuration Requise

### Secrets GitHub Actions

Vous devez configurer les secrets suivants dans votre dépôt GitHub (`Settings > Secrets > Actions`) :

| Nom du Secret | Description | Exemple |
|--------------|-------------|---------|
| `DOCKER_HUB_USERNAME` | Nom d'utilisateur Docker Hub | `votre_utilisateur` |
| `DOCKER_HUB_TOKEN` | Token d'accès Docker Hub | `dckr_pat_...` |
| `PRODUCTION_SERVER` | Adresse IP ou domaine du serveur | `planflan.fr` ou `123.45.67.89` |
| `PRODUCTION_USER` | Utilisateur SSH pour le serveur | `deploy` ou `root` |
| `SSH_PRIVATE_KEY` | Clé privée SSH pour l'accès au serveur | `-----BEGIN RSA PRIVATE KEY-----...` |
| `SLACK_WEBHOOK` | (Optionnel) Webhook Slack pour les notifications | `https://hooks.slack.com/...` |

### Configuration du Serveur de Production

1. **Utilisateur de déploiement** :
   ```bash
   # Créer un utilisateur dédié
   sudo adduser deploy
   sudo usermod -aG sudo deploy
   sudo usermod -aG docker deploy
   
   # Configurer SSH (recommandé : clé SSH uniquement)
   sudo mkdir -p /home/deploy/.ssh
   sudo chown deploy:deploy /home/deploy/.ssh
   sudo chmod 700 /home/deploy/.ssh
   ```

2. **Répertoire du projet** :
   ```bash
   sudo mkdir -p /opt/planflan3
   sudo chown deploy:deploy /opt/planflan3
   ```

3. **Docker et Docker Compose** :
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-plugin
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

4. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-org/planflan3.git /opt/planflan3
   cd /opt/planflan3
   git checkout main
   ```

## 🚀 Utilisation de la Pipeline

### 1. Développement et Tests Locaux

Avant de pousser du code, exécutez localement :

```bash
# Tests rapides
make test-quick

# Tests complets
make test-all

# Tests avec couverture
make test-coverage

# Tests de déploiement (nécessite RUN_DEPLOYMENT_TESTS=true)
make test-deployment
```

### 2. Workflow CI (Intégration Continue)

La pipeline CI s'exécute automatiquement lorsque :

- Vous poussez sur les branches `dev` ou `main`
- Vous modifiez des fichiers Docker ou du code applicatif
- Une pull request est créée ou mise à jour

**Fichiers surveillés** :
- `Dockerfile`
- `docker-compose.yml`
- `entrypoint.sh`
- `app/**`
- `tests/**`

### 3. Workflow CD (Livraison Continue)

La pipeline CD s'exécute automatiquement lorsque :

- Un push est effectué sur la branche `main`
- Le workflow CI se termine avec succès

**Processus de déploiement** :

1. **Récupération du code** : Le serveur distant récupère les dernières modifications
2. **Construction Docker** : Les conteneurs sont reconstruits avec les dernières images
3. **Redémarrage des services** : Les nouveaux conteneurs sont démarrés
4. **Vérification** : Tests post-déploiement pour s'assurer que tout fonctionne
5. **Nettoyage** : Suppression des anciennes images

### 4. Vérifications Pré-déploiement

Le workflow `pre-deploy-checks` s'exécute lorsque :

- Une pull request est créée ou mise à jour
- Un push est effectué sur la branche `dev`

**Vérifications effectuées** :

- ✅ Vérification de la syntaxe Python
- ✅ Linting avec Pylint
- ✅ Analyse de sécurité avec Bandit et Safety
- ✅ Exécution de tous les tests
- ✅ Analyse de couverture de code (minimum 80%)
- ✅ Validation du Dockerfile
- ✅ Vérification des dépendances
- ✅ Détection des secrets dans le code
- ✅ Validation des fichiers de configuration
- ✅ Vérification des workflows GitHub Actions

## 📊 Rapports et Artifacts

### Rapports de Couverture

Les rapports de couverture sont générés et disponibles :

- **Format XML** : `coverage.xml` (pour l'intégration CI)
- **Format HTML** : `htmlcov/` (rapport visuel)
- **Format Terminal** : Affiché dans les logs

### Artifacts Disponibles

Après chaque exécution CI, vous pouvez télécharger :

- **Rapport de couverture** : Fichier `coverage.xml`
- **Logs de test** : Disponibles dans l'interface GitHub Actions
- **Rapport Bandit** : `bandit-report.json` (analyse de sécurité)

## 🔄 Stratégie de Branches

```
main (production) ← dev (intégration) ← feature/* (développement)
```

### Bonnes Pratiques :

1. **Feature branches** : Créez des branches `feature/nom-de-la-feature` pour le développement
2. **Pull Requests** : Toujours créer une PR vers `dev` pour la revue de code
3. **Tests** : Tous les tests doivent passer avant la fusion
4. **Revue** : Au moins un approbateur requis pour les PR
5. **Fusion vers main** : Seule la branche `dev` peut être fusionnée vers `main`

## 🛠 Dépannage

### Problèmes Courants

**1. Échec des tests de déploiement** :
- Vérifiez que le site est accessible
- Assurez-vous que `RUN_DEPLOYMENT_TESTS=true` est défini
- Vérifiez les URLs dans `test_deployment.py`

**2. Échec de la construction Docker** :
- Vérifiez la syntaxe du `Dockerfile`
- Assurez-vous que toutes les dépendances sont listées dans `requirements.txt`
- Vérifiez les permissions du script `entrypoint.sh`

**3. Échec de déploiement** :
- Vérifiez les secrets GitHub Actions
- Assurez-vous que le serveur est accessible
- Vérifiez les logs SSH et Docker sur le serveur

**4. Problèmes de couverture** :
- Exécutez `make test-coverage` localement
- Identifiez les fichiers avec faible couverture
- Ajoutez des tests pour les zones non couvertes

## 📈 Améliorations Futures

- Ajouter des tests de performance
- Intégrer des tests d'accessibilité
- Configurer des notifications avancées (Slack, Email)
- Ajouter des tests de charge
- Configurer un environnement de staging

## 📚 Documentation Complémentaire

- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Guide Docker](https://docs.docker.com/)
- [Documentation Pytest](https://docs.pytest.org/)
- [Guide de Sécurité Python](https://bandit.readthedocs.io/)

---

*Dernière mise à jour : 14 janvier 2026*
*Version : 1.0*