# Guide de déploiement - Fix des photos Google Places

## Résumé des changements

Le système de téléchargement des photos Google Places a été corrigé pour fonctionner correctement en production avec Docker. Les modifications standardisent les chemins et garantissent que les photos sont correctement téléchargées et persistées.

## Fichiers modifiés

### 1. **Dockerfile**
- WORKDIR changé de `/python-docker` → `/app`
- Création du dossier `/app/static/uploads` avec permissions 777
- Mise à jour des chemins de l'entrypoint

### 2. **docker-compose.yml**
- Volume `photos_volume` monté sur `/app/static/uploads` (au lieu de l'ancien chemin)
- Volume `scripts` monté sur `/app/scripts`

### 3. **entrypoint.sh**
- Vérification de l'existence du dossier uploads au démarrage
- Test d'écriture pour confirmer les permissions
- Logs détaillés pour diagnostic

### 4. **app/configprod.py**
- `UPLOAD_FOLDER` utilise un chemin absolu calculé dynamiquement
- Compatible Docker et développement local

### 5. **app/outils.py** (fonction `fetch_place_photos`)
- Logs détaillés préfixés `[FETCH_PHOTOS]` à chaque étape
- Vérification et création automatique du dossier uploads si nécessaire
- Vérification des permissions d'écriture
- Meilleure gestion des erreurs avec traceback complet
- Vérification de l'existence du fichier après sauvegarde

### 6. **nginx/default.conf**
- Ajout de `location /static/uploads/` pour servir les fichiers via nginx
- Configuration HTTP et HTTPS

### 7. **tests/test_scenario_photos.py**
- Ajout de tests pour valider la configuration UPLOAD_FOLDER
- Test de vérification des permissions d'écriture
- Test de création automatique du dossier uploads
- **✅ 10/10 tests passent**

## Procédure de déploiement

### Étape 1 : Sauvegarder les photos existantes (si applicable)

```bash
# Sur le serveur de production
docker exec planflan-container-backend tar -czf /tmp/photos_backup.tar.gz -C /app/static uploads/
docker cp planflan-container-backend:/tmp/photos_backup.tar.gz ~/backups/photos_$(date +%Y%m%d).tar.gz
```

### Étape 2 : Arrêter les conteneurs

```bash
docker-compose down
```

### Étape 3 : Reconstruire l'image Docker

```bash
# Rebuild sans --no-cache pour forcer la reconstruction complète
docker-compose build planflan-backend
```

### Étape 4 : Démarrer les conteneurs

```bash
docker-compose up -d
```

### Étape 5 : Vérifier les logs de démarrage

```bash
docker logs planflan-container-backend | grep -A5 "Vérification du dossier uploads"
```

Vous devriez voir :
```
Vérification du dossier uploads...
Test d'écriture dans /app/static/uploads
✓ Dossier uploads accessible en écriture
```

### Étape 6 : Restaurer les photos (si applicable)

```bash
docker cp ~/backups/photos_XXXXXXXX.tar.gz planflan-container-backend:/tmp/
docker exec planflan-container-backend tar -xzf /tmp/photos_XXXXXXXX.tar.gz -C /app/static/
docker exec planflan-container-backend rm /tmp/photos_XXXXXXXX.tar.gz
```

### Étape 7 : Tester la création d'un établissement

1. Connectez-vous à l'application
2. Créez un nouvel établissement avec un `google_place_id`
3. Vérifiez les logs en temps réel :

```bash
docker logs -f planflan-container-backend | grep FETCH_PHOTOS
```

Vous devriez voir :
```
[FETCH_PHOTOS] Début pour établissement X, place_id=ChIJ...
[FETCH_PHOTOS] UPLOAD_FOLDER configuré: /app/static/uploads
[FETCH_PHOTOS] ✓ Permission d'écriture OK sur /app/static/uploads
[FETCH_PHOTOS] Téléchargement photo 0, reference=...
[FETCH_PHOTOS] Réponse API: status_code=200
[FETCH_PHOTOS] Sauvegarde dans: /app/static/uploads/ChIJ...photo_0.jpg
[FETCH_PHOTOS] ✓ Fichier créé avec succès, taille=XXXX octets
[FETCH_PHOTOS] Photo ajoutée en base: ChIJ...photo_0.jpg
[FETCH_PHOTOS] Terminé, 1 photo(s) sauvegardée(s)
```

### Étape 8 : Vérifier que la photo s'affiche

1. Rechargez la page de l'établissement
2. La photo Google devrait s'afficher (pas la photo par défaut)
3. Inspectez l'élément `<img>` dans le navigateur (F12)
4. L'URL devrait être : `/static/uploads/ChIJ...photo_0.jpg`

### Étape 9 : Vérifier dans le volume Docker

```bash
# Lister les fichiers dans le dossier uploads
docker exec planflan-container-backend ls -lh /app/static/uploads/

# Vérifier qu'un fichier spécifique existe
docker exec planflan-container-backend ls -lh /app/static/uploads/ | grep ChIJ
```

## Diagnostic en cas de problème

### Problème : La photo ne se télécharge pas

```bash
# 1. Vérifier que le dossier existe et a les bonnes permissions
docker exec planflan-container-backend ls -la /app/static/

# 2. Vérifier la clé API Google
docker exec planflan-container-backend env | grep GOOGLE_MAPS_API_KEY

# 3. Tester l'écriture manuellement
docker exec planflan-container-backend touch /app/static/uploads/test_manual.txt
docker exec planflan-container-backend ls -la /app/static/uploads/test_manual.txt

# 4. Vérifier les logs détaillés
docker logs planflan-container-backend | grep -A20 "\[FETCH_PHOTOS\]"

# 5. Vérifier la base de données
docker exec planflan-container-db mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  -e "SELECT id_photo, id_etab, path FROM photos ORDER BY id_photo DESC LIMIT 5;"
```

### Problème : La photo se télécharge mais ne s'affiche pas

```bash
# 1. Vérifier que le fichier existe
docker exec planflan-container-backend ls -la /app/static/uploads/ | grep ChIJ

# 2. Vérifier la taille du fichier (ne devrait pas être 0)
docker exec planflan-container-backend du -h /app/static/uploads/ChIJ*

# 3. Dans le navigateur (F12 > Network)
# Chercher les requêtes vers /static/uploads/
# Vérifier s'il y a des erreurs 404 ou 403

# 4. Vérifier les logs nginx
docker logs planflan-container-nginx | grep static/uploads

# 5. Tester l'accès direct à l'image
curl -I https://planflan.fr/static/uploads/ChIJ...photo_0.jpg
```

### Problème : Erreur de permissions

```bash
# 1. Vérifier les permissions du dossier
docker exec planflan-container-backend stat /app/static/uploads

# 2. Corriger les permissions si nécessaire
docker exec planflan-container-backend chmod -R 777 /app/static/uploads

# 3. Vérifier l'utilisateur qui exécute l'application
docker exec planflan-container-backend whoami
docker exec planflan-container-backend id
```

## Rollback (si nécessaire)

Si vous rencontrez des problèmes critiques, vous pouvez revenir à la version précédente :

```bash
# 1. Arrêter les conteneurs
docker-compose down

# 2. Checkout de la version précédente
git checkout <commit-hash-precedent>

# 3. Reconstruire et redémarrer
docker-compose build planflan-backend
docker-compose up -d

# 4. Restaurer les photos sauvegardées
docker cp ~/backups/photos_XXXXXXXX.tar.gz planflan-container-backend:/tmp/
docker exec planflan-container-backend tar -xzf /tmp/photos_XXXXXXXX.tar.gz -C /app/static/
```

## Vérifications post-déploiement

- [ ] Le conteneur démarre sans erreur
- [ ] Le message "✓ Dossier uploads accessible en écriture" apparaît dans les logs
- [ ] La création d'un établissement génère des logs `[FETCH_PHOTOS]`
- [ ] Le fichier photo est créé dans `/app/static/uploads/`
- [ ] L'enregistrement est créé dans la table `photos`
- [ ] La photo s'affiche sur la carte de l'établissement
- [ ] Aucune erreur 404 dans les logs nginx pour `/static/uploads/`

## Support

En cas de problème persistant :

1. Collectez les logs complets :
```bash
docker logs planflan-container-backend > ~/logs/backend_$(date +%Y%m%d_%H%M%S).log
docker logs planflan-container-nginx > ~/logs/nginx_$(date +%Y%m%d_%H%M%S).log
```

2. Vérifiez l'état du volume Docker :
```bash
docker volume inspect planflan2_photos_volume
```

3. Consultez la documentation complète dans `PHOTO_UPLOAD_FIX.md`
