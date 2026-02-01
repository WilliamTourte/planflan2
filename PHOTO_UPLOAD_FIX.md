# Fix du téléchargement des photos Google Places en production

## Problème
Les photos Google Places étaient téléchargées en développement mais pas en production Docker.

## Causes identifiées

1. **Conflit de WORKDIR** : Le Dockerfile utilisait `/python-docker` mais les volumes étaient montés sur `/app`
2. **Dossier uploads non créé** : Le dossier `static/uploads` n'était jamais créé dans le conteneur
3. **Permissions manquantes** : Pas de permissions d'écriture sur le dossier uploads
4. **Chemin relatif** : La config production utilisait un chemin relatif qui ne se résolvait pas correctement

## Corrections appliquées

### 1. Dockerfile
- WORKDIR standardisé à `/app` (au lieu de `/python-docker`)
- Création du dossier `/app/static/uploads` avec permissions 777
- Mise à jour des chemins de l'entrypoint

### 2. entrypoint.sh
- Ajout d'une vérification du dossier uploads au démarrage
- Test d'écriture pour confirmer les permissions
- Logs pour diagnostic

### 3. docker-compose.yml
- Volume `photos_volume` monté sur `/app/static/uploads` (au lieu de l'ancien chemin)
- Volume scripts monté sur `/app/scripts`

### 4. app/configprod.py
- UPLOAD_FOLDER utilise maintenant un chemin absolu calculé dynamiquement
- Compatible avec Docker et développement local

### 5. app/outils.py (fetch_place_photos)
- Logs détaillés à chaque étape du téléchargement
- Vérification de l'existence et des permissions du dossier uploads
- Création automatique du dossier si nécessaire
- Meilleure gestion des erreurs avec traceback complet

### 6. nginx/default.conf
- Location `/static/uploads/` ajoutée pour servir les fichiers via nginx
- Améliore les performances en évitant de passer par Flask

## Comment tester

### En développement
```bash
python run.py
# Créer un établissement avec un google_place_id
# Vérifier que la photo apparaît dans static/uploads/
```

### En production (Docker)
```bash
# Reconstruire l'image Docker
docker-compose build planflan-backend

# Redémarrer les conteneurs
docker-compose down
docker-compose up -d

# Vérifier les logs au démarrage
docker logs planflan-container-backend | grep "uploads"

# Devrait afficher :
# ✓ Dossier uploads accessible en écriture

# Créer un établissement et vérifier les logs
docker logs -f planflan-container-backend | grep FETCH_PHOTOS

# Vérifier que le fichier existe dans le volume
docker exec planflan-container-backend ls -la /app/static/uploads/
```

## Vérifications post-déploiement

1. ✅ Le dossier `/app/static/uploads/` existe dans le conteneur
2. ✅ Le conteneur peut écrire dans ce dossier (test_write.txt créé puis supprimé)
3. ✅ Les photos Google sont téléchargées et sauvegardées
4. ✅ Les enregistrements sont créés dans la table `photos`
5. ✅ Les images s'affichent sur les cartes d'établissements
6. ✅ Les logs `[FETCH_PHOTOS]` montrent toutes les étapes

## Structure attendue

```
/app/static/uploads/
├── ChIJxxxx_photo_0.jpg  (photos Google Places)
├── ChIJyyyy_photo_0.jpg
├── defaut_etab.jpg        (photo par défaut)
└── flan-vanille.webp      (photo par défaut flan)
```

## En cas de problème

### La photo ne se télécharge pas
```bash
# Vérifier les logs détaillés
docker logs planflan-container-backend | grep FETCH_PHOTOS

# Vérifier la clé API Google
docker exec planflan-container-backend env | grep GOOGLE_MAPS_API_KEY

# Vérifier les permissions
docker exec planflan-container-backend ls -la /app/static/
docker exec planflan-container-backend touch /app/static/uploads/test.txt
```

### L'image ne s'affiche pas
```bash
# Vérifier que le fichier existe
docker exec planflan-container-backend ls -la /app/static/uploads/ | grep ChIJ

# Vérifier dans la base de données
docker exec planflan-container-db mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT * FROM photos ORDER BY id DESC LIMIT 5;"

# Vérifier dans le navigateur (F12 > Network)
# Chercher les erreurs 404 sur /static/uploads/xxx.jpg
```

## Améliorations futures possibles

1. **Cache nginx** : Ajouter du cache pour les fichiers uploads
2. **CDN** : Utiliser un CDN pour servir les images
3. **Optimisation d'images** : Compresser les images téléchargées
4. **Fallback** : Si l'API Google échoue, utiliser une photo par défaut
5. **Retry logic** : Réessayer le téléchargement en cas d'échec temporaire
