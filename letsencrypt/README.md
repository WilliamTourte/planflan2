# Scripts Certbot pour PlanFlan

Ce dossier contient les scripts pour gérer les certificats SSL avec Let's Encrypt.

## Fichiers

- `obtain-certificates.sh` : Obtient les certificats initiaux
- `renew-certificates.sh` : Renouvelle les certificats existants
- `test-certificates.sh` : Teste l'obtention des certificats (mode dry-run)
- `setup-cron.sh` : Configure le renouvellement automatique

## Utilisation

### 1. Test initial (recommandé)
```bash
./test-certificates.sh
```

### 2. Obtention des certificats
```bash
./obtain-certificates.sh
```

### 3. Configuration du renouvellement automatique
```bash
./setup-cron.sh
```

## Configuration requise

1. **DNS** : Assurez-vous que votre domaine (planflan.fr) et www.planflan.fr pointent vers l'IP de votre serveur (51.210.4.227)
2. **Email** : Remplacez `votre@email.com` par votre adresse email dans les scripts
3. **Pare-feu** : Les ports 80 (HTTP) et 443 (HTTPS) doivent être ouverts sur votre serveur
4. **Fichier .env** : Doit être présent sur le serveur avec les bonnes valeurs

## Recommandations pour le déploiement

### 1. Préparation du serveur
```bash
# Ouvrir les ports nécessaires
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Vérifier le DNS
dig planflan.fr
dig www.planflan.fr
```

### 2. Procédure de déploiement
```bash
# 1. Copier les fichiers sur le serveur
docker compose down
scp -r /chemin/local/planflan2 user@51.210.4.227:/chemin/serveur/planflan2

# 2. Se connecter au serveur
ssh user@51.210.4.227
cd /chemin/serveur/planflan2

# 3. Construire et démarrer les services de base
docker compose up -d --build planflan-service-db planflan-backend

# 4. Tester l'obtention des certificats (mode dry-run)
./letsencrypt/test-certificates.sh

# 5. Obtenir les certificats réels
./letsencrypt/obtain-certificates.sh

# 6. Démarrer Nginx
docker compose up -d nginx

# 7. Configurer le renouvellement automatique
./letsencrypt/setup-cron.sh
```

### 3. Vérifications post-déploiement
```bash
# Vérifier que tous les conteneurs sont en cours d'exécution
docker compose ps

# Vérifier les logs
docker compose logs -f

# Tester la configuration Nginx
docker compose exec nginx nginx -t

# Tester la connectivité
curl -I http://localhost
curl -I https://localhost

# Vérifier les certificats obtenus
docker compose exec certbot ls -la /etc/letsencrypt/live/planflan.fr/
```

## Dépannage

### Problèmes courants et solutions

1. **Connection refused sur le port 80**
   - Vérifiez que Nginx est en cours d'exécution : `docker compose ps`
   - Vérifiez les logs : `docker compose logs nginx`
   - Testez la configuration : `docker compose exec nginx nginx -t`

2. **Erreur DNS**
   - Vérifiez que votre domaine pointe vers la bonne IP
   - Attendez la propagation DNS (peut prendre jusqu'à 24h)

3. **Problèmes de certificats**
   - Vérifiez les logs Certbot : `docker compose logs certbot`
   - Testez avec `--dry-run` avant d'obtenir les certificats réels

4. **Pare-feu bloquant**
   - Vérifiez les règles : `sudo ufw status`
   - Ouvrez les ports : `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`

### Commandes utiles

```bash
# Vérifier les ports écoutés
sudo netstat -tulnp | grep :80
sudo ss -tulnp | grep :80

# Tester depuis le conteneur
docker compose exec nginx apk add curl
docker compose exec nginx curl -I http://localhost

# Recharger la configuration Nginx
docker compose exec nginx nginx -s reload

# Voir les certificats obtenus
docker compose exec certbot ls -la /etc/letsencrypt/live/
```

## Bonnes pratiques

1. **Sauvegarde**
   - Sauvegardez régulièrement vos certificats
   - Sauvegardez votre base de données avant les mises à jour

2. **Sécurité**
   - Limitez les permissions sur les fichiers de configuration
   - Ne versionnez pas les fichiers sensibles (.env, certificats)

3. **Monitoring**
   - Configurez des alertes pour le renouvellement des certificats
   - Surveillez les logs de Nginx et Certbot
   - Utilisez `docker compose logs -f` pour le débogage en temps réel

4. **Mises à jour**
   - Mettez régulièrement à jour vos images Docker
   - Testez les mises à jour en environnement de staging avant la production

## Notes importantes

- Les certificats Let's Encrypt expirent après 90 jours
- Le renouvellement automatique est configuré pour s'exécuter deux fois par jour
- Utilisez toujours `--dry-run` pour les tests avant d'obtenir des certificats réels
- Les limites de Let's Encrypt : 5 certificats par domaine par semaine (en production)
