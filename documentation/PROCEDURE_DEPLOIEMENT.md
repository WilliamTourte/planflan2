# Configuration des Clés pour la Pipeline CI/CD

Ce guide complet explique comment configurer toutes les clés et secrets nécessaires pour faire fonctionner votre pipeline CI/CD PlanFlan.

## 🎯 Objectif

Configurer en toute sécurité :
- L'accès à Docker Hub pour les images
- La connexion SSH au serveur de production
- Les secrets GitHub Actions pour l'automatisation
- Les variables d'environnement nécessaires

## 🔑 Configuration des Clés et Secrets

### 1. Docker Hub (pour les images Docker)

#### 🎯 Créer un token Docker Hub

1. **Connectez-vous à Docker Hub** : [https://hub.docker.com/](https://hub.docker.com/)

2. **Créez un token d'accès** :
   - Allez dans `Account Settings` → `Security`
   - Cliquez sur `New Access Token`
   - Donnez-lui un nom : `planflan-ci-cd`
   - Sélectionnez les permissions : `Read & Write`
   - Copiez le token généré (vous ne pourrez plus le voir après)

3. **Notez vos identifiants** :
   - `DOCKER_HUB_USERNAME` : Votre nom d'utilisateur Docker
   - `DOCKER_HUB_TOKEN` : Le token que vous venez de créer

#### 📌 Bonnes pratiques Docker Hub

- Utilisez un token dédié à la CI/CD
- Ne jamais utiliser votre mot de passe Docker Hub directement
- Rotatez le token tous les 6 mois
- Limitez les permissions au strict nécessaire (`Read & Write` suffit)

---

### 2. Serveur de Production (pour le déploiement)

#### 🎯 Préparer l'accès SSH

1. **Créez un utilisateur dédié** (sur votre serveur) :
   ```bash
   sudo adduser deploy
   sudo usermod -aG sudo deploy
   sudo usermod -aG docker deploy
   ```

2. **Générez une clé SSH** (sur votre machine locale) :
   ```bash
   ssh-keygen -t rsa -b 4096 -C "deploy@planflan.fr"
   # Ne mettez pas de passphrase pour l'automatisation
   # Enregistrez dans ~/.ssh/id_rsa_deploy
   ```

3. **Installez la clé publique sur le serveur** :
   ```bash
   # Copiez la clé publique
   cat ~/.ssh/id_rsa_deploy.pub
   
   # Sur le serveur, ajoutez-la à l'utilisateur deploy
   sudo mkdir -p /home/deploy/.ssh
   sudo touch /home/deploy/.ssh/authorized_keys
   sudo chmod 600 /home/deploy/.ssh/authorized_keys
   sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
   # Collez la clé publique dans ce fichier
   ```

4. **Sécurisez le serveur** :
   ```bash
   # Sur le serveur
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart sshd
   ```

5. **Notez vos informations serveur** :
   - `PRODUCTION_SERVER` : IP ou domaine (ex: `planflan.fr` ou `123.45.67.89`)
   - `PRODUCTION_USER` : `deploy`
   - `SSH_PRIVATE_KEY` : Contenu de `~/.ssh/id_rsa_deploy` (clé privée)

#### 📌 Bonnes pratiques SSH

- Utilisez toujours des clés SSH plutôt que des mots de passe
- Désactivez l'authentification par mot de passe sur le serveur
- Utilisez des clés de 4096 bits pour une meilleure sécurité
- Ne jamais partager votre clé privée
- Protégez votre clé privée avec `chmod 600 ~/.ssh/id_rsa_deploy`

---

### 3. GitHub Secrets (pour la pipeline)

#### 🎯 Configurer les secrets dans GitHub

1. **Allez dans votre dépôt GitHub** :
   - `Settings` → `Secrets and variables` → `Actions`

2. **Ajoutez les secrets suivants** :

| Nom du Secret | Valeur | Description | Exemple |
|--------------|--------|-------------|---------|
| `DOCKER_HUB_USERNAME` | Votre username Docker | Pour pousser les images | `mon_utilisateur` |
| `DOCKER_HUB_TOKEN` | Le token Docker généré | Accès à Docker Hub | `dckr_pat_...` |
| `PRODUCTION_SERVER` | IP ou domaine du serveur | Où déployer | `planflan.fr` |
| `PRODUCTION_USER` | `deploy` | Utilisateur SSH | `deploy` |
| `SSH_PRIVATE_KEY` | Clé privée SSH complète | Pour la connexion | `-----BEGIN RSA...` |
| `SLACK_WEBHOOK` | (Optionnel) Webhook Slack | Notifications | `https://hooks.slack.com/...` |

3. **Comment ajouter la clé SSH** :
   - Ouvrez le fichier de clé privée : `cat ~/.ssh/id_rsa_deploy`
   - Copiez TOUT le contenu (y compris les lignes `-----BEGIN RSA PRIVATE KEY-----` et `-----END RSA PRIVATE KEY-----`)
   - Collez-le dans le secret `SSH_PRIVATE_KEY`

#### 📌 Bonnes pratiques GitHub Secrets

- Utilisez des noms de secrets clairs et descriptifs
- Ne jamais exposer les secrets dans les logs
- Utilisez le masquage automatique de GitHub pour les secrets
- Limitez l'accès aux secrets aux collaborateurs nécessaires
- Rotatez les secrets régulièrement

---

### 4. Configuration Locale (pour les tests)

#### 🎯 Configurer votre environnement local

1. **Créez un fichier `.env` local** :
   ```bash
   cp .env.example .env  # Si vous avez un exemple
   ```

2. **Configurez les variables nécessaires** :
   ```ini
   # .env
   MYSQL_USER=test_user
   MYSQL_PASSWORD=test_password
   MYSQL_DATABASE=test_db
   MYSQL_ROOT_PASSWORD=root_password
   FLASK_SECRET_KEY=votre_cle_secrete_ici
   
   # Pour le développement local
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

3. **Ajoutez `.env` à `.gitignore`** :
   ```bash
   echo ".env" >> .gitignore
   echo "*.pem" >> .gitignore
   echo "*.key" >> .gitignore
   ```

#### 📌 Bonnes pratiques Variables d'Environnement

- Ne jamais commiter `.env` dans Git
- Utilisez des valeurs différentes pour dev/prod
- Documentez les variables nécessaires dans un `.env.example`
- Utilisez des valeurs sécurisées pour les secrets
- Rotatez les secrets régulièrement

---

## 📋 Checklist de Configuration Complète

### ✅ Configuration Docker Hub
- [ ] Compte Docker Hub créé
- [ ] Token d'accès généré (`Read & Write`)
- [ ] Token testé localement
- [ ] Nom d'utilisateur et token notés

### ✅ Configuration Serveur
- [ ] Utilisateur `deploy` créé
- [ ] Clé SSH générée (4096 bits)
- [ ] Clé publique installée sur le serveur
- [ ] Authentification par mot de passe désactivée
- [ ] Connexion SSH testée

### ✅ Configuration GitHub
- [ ] Secrets `DOCKER_HUB_USERNAME` ajouté
- [ ] Secrets `DOCKER_HUB_TOKEN` ajouté
- [ ] Secrets `PRODUCTION_SERVER` ajouté
- [ ] Secrets `PRODUCTION_USER` ajouté
- [ ] Secrets `SSH_PRIVATE_KEY` ajouté
- [ ] Accès aux secrets vérifié

### ✅ Configuration Locale
- [ ] Fichier `.env` créé
- [ ] Variables nécessaires configurées
- [ ] `.env` ajouté à `.gitignore`
- [ ] Test local réussi

---

## 🛠 Commandes Utiles

### Vérification des Connexions

```bash
# Tester la connexion Docker Hub
echo $DOCKER_HUB_TOKEN | docker login -u $DOCKER_HUB_USERNAME --password-stdin

# Tester la connexion SSH (avec la clé)
ssh -i ~/.ssh/id_rsa_deploy deploy@PRODUCTION_SERVER

# Tester la connexion SSH (sans clé, si configuré)
ssh deploy@PRODUCTION_SERVER
```

### Gestion des Clés SSH

```bash
# Générer une nouvelle clé SSH
ssh-keygen -t rsa -b 4096 -C "votre_email@example.com"

# Afficher la clé publique
cat ~/.ssh/id_rsa_deploy.pub

# Afficher la clé privée (pour GitHub Secrets)
cat ~/.ssh/id_rsa_deploy

# Changer les permissions de la clé privée
chmod 600 ~/.ssh/id_rsa_deploy

# Ajouter la clé à l'agent SSH
ssh-add ~/.ssh/id_rsa_deploy
```

### Gestion Docker

```bash
# Construire une image localement
docker build -t planflan.backend:test .

# Tester le conteneur localement
docker run --name test-container -d -p 5000:5000 planflan.backend:test

# Voir les logs
docker logs test-container

# Arrêter le conteneur
docker stop test-container

# Supprimer le conteneur
docker rm test-container

# Lister les images
docker images

# Supprimer une image
docker rmi planflan.backend:test
```

### Gestion GitHub Secrets

```bash
# Lister les secrets (nécessite gh CLI)
gh secret list

# Vérifier l'accès aux secrets
gh api /repos/{owner}/{repo}/actions/secrets

# Tester un workflow manuellement
gh workflow run ci.yml
```

---

## 🚀 Procédure de Test Complète

### 1. Test Local

```bash
# Tester la construction Docker
docker build --no-cache -t planflan.backend:test .

# Tester le démarrage
docker run --name test-container -d -p 5000:5000 planflan.backend:test

# Vérifier que l'application répond
curl http://localhost:5000

# Arrêter et nettoyer
docker stop test-container
docker rm test-container
```

### 2. Test de Connexion au Serveur

```bash
# Tester la connexion SSH
ssh -i ~/.ssh/id_rsa_deploy deploy@PRODUCTION_SERVER

# Tester Docker sur le serveur
ssh deploy@PRODUCTION_SERVER "docker --version"

# Tester git sur le serveur
ssh deploy@PRODUCTION_SERVER "git --version"
```

### 3. Test de la Pipeline CI

```bash
# Créer une branche de test
git checkout -b test/ci-setup

# Faire un petit changement
echo "# Test CI Setup" >> README.md

# Commiter et pousser
git add README.md
git commit -m "Test: Configuration CI"
git push origin test/ci-setup

# Aller sur GitHub et vérifier que la pipeline se déclenche
```

### 4. Test de Déploiement (sans déploiement réel)

```bash
# Sur une branche test, simuler le déploiement
# La pipeline CD ne devrait pas se déclencher (branche != main)

# Vérifier que les étapes de pré-déploiement passent
git push origin test/ci-setup
```

---

## ⚠️ Résolution des Problèmes Courants

### Problème 1: Échec de la connexion Docker Hub

**Symptômes** :
- `Error: Cannot perform an interactive login from a non TTY device`
- `Authentication failed`

**Solutions** :
1. Vérifiez que le token est valide
2. Régénérez le token si nécessaire
3. Vérifiez les permissions du token
4. Testez manuellement : `docker login -u USERNAME -p TOKEN`

### Problème 2: Échec de la connexion SSH

**Symptômes** :
- `Permission denied (publickey)`
- `Connection refused`

**Solutions** :
1. Vérifiez que la clé publique est bien sur le serveur
2. Vérifiez les permissions : `chmod 600 ~/.ssh/id_rsa_deploy`
3. Testez avec `ssh -v -i ~/.ssh/id_rsa_deploy deploy@SERVER`
4. Vérifiez que l'utilisateur `deploy` existe sur le serveur
5. Vérifiez que le serveur SSH écoute : `sudo systemctl status sshd`

### Problème 3: Échec de la construction Docker

**Symptômes** :
- `Build failed`
- `Error: Unable to build image`

**Solutions** :
1. Testez la construction localement d'abord
2. Vérifiez la syntaxe du Dockerfile
3. Vérifiez que toutes les dépendances sont dans `requirements.txt`
4. Vérifiez les permissions du script `entrypoint.sh`

### Problème 4: Pipeline ne se déclenche pas

**Symptômes** :
- Push effectué mais pas de pipeline
- Pas de workflow visible dans GitHub Actions

**Solutions** :
1. Vérifiez que vous avez poussé sur `dev` ou `main`
2. Vérifiez que les fichiers modifiés sont dans les paths surveillés
3. Vérifiez les permissions du dépôt
4. Vérifiez que GitHub Actions est activé pour le dépôt

---

## 🎓 Bonnes Pratiques de Sécurité

### 1. Rotation des Secrets

```bash
# Rotatez les tokens Docker tous les 6 mois
# Rotatez les clés SSH annuellement

# Pour rotatez un token Docker :
1. Créez un nouveau token
2. Mettez à jour le secret GitHub
3. Supprimez l'ancien token
```

### 2. Audit Régulier

```bash
# Vérifiez régulièrement :
- Qui a accès aux secrets
- Quels workflows utilisent les secrets
- Les permissions des tokens

# Utilisez l'audit log GitHub
```

### 3. Principes de Moindre Privilège

- Donnez seulement les permissions nécessaires
- Limitez l'accès aux secrets
- Utilisez des comptes dédiés (pas vos comptes personnels)

### 4. Sauvegarde des Secrets

- Stockez les secrets dans un gestionnaire de mots de passe
- Partagez les secrets de manière sécurisée
- Ne stockez pas les secrets en clair

---

## 📅 Plan de Maintenance

| Période | Action | Responsable |
|---------|--------|-------------|
| Hebdomadaire | Vérifier les logs GitHub Actions | Équipe Dev |
| Mensuelle | Vérifier l'espace Docker Hub | Équipe Dev |
| Trimestrielle | Audit des accès aux secrets | Admin |
| Semestrielle | Rotation des tokens Docker | Admin |
| Annuelle | Rotation des clés SSH | Admin |

---

## 📚 Ressources Complémentaires

- [Documentation Docker Hub Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [Guide SSH GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Guide GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Bonnes pratiques sécurité SSH](https://www.ssh.com/academy/ssh/security)
- [Guide sécurité Docker](https://docs.docker.com/engine/security/)

---

## 🎉 Validation Finale

Une fois tout configuré :

1. **Testez chaque composant individuellement**
2. **Testez l'intégration complète**
3. **Documentez la configuration**
4. **Formez l'équipe**
5. **Surveillez les premiers déploiements**

**Votre pipeline CI/CD est maintenant prête à être utilisée en production !** 🚀

---

*Dernière mise à jour : 14 janvier 2026*
*Version : 1.0*
*Responsable : Équipe DevOps PlanFlan*