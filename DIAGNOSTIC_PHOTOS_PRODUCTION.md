# 🔍 Diagnostic : Photos Google Places ne s'affichent pas en PRODUCTION

## 🎯 Problème

Les photos Google Places fonctionnent en **Docker local** mais **pas en production** sur le serveur.

## 📋 Checklist de diagnostic (à exécuter sur le serveur de production)

### 1. Vérifier que les conteneurs sont actifs

```bash
# Sur le serveur de production
docker compose ps
```

**Attendu :** Les 3 conteneurs (backend, nginx, db) doivent être "Up"

---

### 2. Vérifier la clé API Google Maps

```bash
# Sur le serveur
grep GOOGLE_MAPS_API_KEY /home/damien/PycharmProjects/planflan2/.env
```

**Questions :**
- ✅ La clé API est-elle définie ?
- ✅ Est-ce la même clé qu'en local (où ça fonctionne) ?
- ✅ La clé a-t-elle des restrictions dans la console Google Cloud ?

**Important :** Vérifiez dans [Google Cloud Console](https://console.cloud.google.com/apis/credentials) :
- Aller dans "APIs & Services" > "Credentials"
- Cliquer sur votre clé API
- Section "API restrictions" : doit inclure **Places API**
- Section "Application restrictions" : 
  - Si "HTTP referrers" est sélectionné, vérifiez que `planflan.fr` et `www.planflan.fr` sont autorisés
  - Si "IP addresses" est sélectionné, ajoutez l'IP de votre serveur

---

### 3. Examiner les logs FETCH_PHOTOS

```bash
# Sur le serveur
docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | tail -30
```

**Ce que vous devriez voir si tout fonctionne :**
```
[FETCH_PHOTOS] Début pour établissement X, place_id=ChIJ...
[FETCH_PHOTOS] Appel de get_place_details pour place_id=ChIJ...
[FETCH_PHOTOS] 1 photo(s) disponible(s) dans l'API Google
[FETCH_PHOTOS] UPLOAD_FOLDER configuré: /app/static/uploads
[FETCH_PHOTOS] ✓ Permission d'écriture OK sur /app/static/uploads
[FETCH_PHOTOS] Téléchargement photo 0, reference=...
[FETCH_PHOTOS] Réponse API: status_code=200
[FETCH_PHOTOS] Sauvegarde dans: /app/static/uploads/ChIJ..._photo_0.jpg
[FETCH_PHOTOS] ✓ Fichier créé avec succès, taille=XXXXX octets
[FETCH_PHOTOS] Photo ajoutée en base: ChIJ..._photo_0.jpg
[FETCH_PHOTOS] Terminé, 1 photo(s) sauvegardée(s)
```

**Scénarios d'erreur possibles :**

#### A. Aucun log FETCH_PHOTOS
→ Le code n'est jamais appelé. Vérifiez que `google_place_id` est bien renseigné lors de la création.

#### B. "Aucune photo trouvée dans les détails de l'établissement"
→ L'API Google ne retourne pas de photos. Causes possibles :
- Clé API invalide ou expirée
- API Places pas activée pour cette clé
- Restrictions sur la clé API

#### C. "Erreur API Google: status=403"
→ Clé API refusée. Vérifiez les restrictions dans Google Cloud Console.

#### D. "Erreur API Google: status=400"
→ Requête invalide (photo_reference incorrect ou expiré)

#### E. "✗ Pas de permission d'écriture"
→ Problème de permissions sur le volume Docker (voir section 4)

---

### 4. Vérifier le volume uploads

```bash
# Sur le serveur - Vérifier le dossier dans le conteneur
docker exec planflan-container-backend ls -lah /app/static/uploads/

# Tester l'écriture
docker exec planflan-container-backend touch /app/static/uploads/test.txt
docker exec planflan-container-backend rm /app/static/uploads/test.txt
```

**Attendu :** 
- Le dossier existe
- Les permissions permettent l'écriture (drwxrwxrwx ou 777)
- Vous voyez des fichiers .jpg si des photos ont été téléchargées

**Si le dossier n'existe pas ou n'est pas accessible :**
```bash
# Recréer le dossier et fixer les permissions
docker exec planflan-container-backend mkdir -p /app/static/uploads
docker exec planflan-container-backend chmod -R 777 /app/static/uploads
```

---

### 5. Vérifier le volume dans nginx

```bash
# Sur le serveur - Vérifier que nginx a accès aux photos
docker exec planflan-container-nginx ls -lah /var/www/uploads/
```

**Attendu :** Vous devez voir les mêmes fichiers que dans le backend.

**Si nginx n'a pas accès :**
→ Le volume n'est pas correctement monté. Vérifiez le `docker-compose.yml` en production.

---

### 6. Vérifier la configuration UPLOAD_FOLDER

```bash
# Sur le serveur
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print('UPLOAD_FOLDER:', app.config['UPLOAD_FOLDER'])
    print('Existe:', os.path.exists(app.config['UPLOAD_FOLDER']))
    print('Écriture:', os.access(app.config['UPLOAD_FOLDER'], os.W_OK))
    print('GOOGLE_MAPS_API_KEY définie:', bool(app.config.get('GOOGLE_MAPS_API_KEY')))
"
```

**Attendu :**
```
UPLOAD_FOLDER: /app/static/uploads
Existe: True
Écriture: True
GOOGLE_MAPS_API_KEY définie: True
```

---

### 7. Tester l'accès HTTP aux photos

```bash
# Sur le serveur - Lister les photos téléchargées
docker exec planflan-container-backend ls /app/static/uploads/*.jpg 2>/dev/null

# Depuis votre machine locale - Tester l'accès via HTTPS
curl -I https://planflan.fr/static/uploads/NOM_PHOTO.jpg
```

**Attendu si la photo est accessible :**
```
HTTP/2 200
server: nginx
content-type: image/jpeg
cache-control: public, immutable
```

**Si 404 Not Found :**
- La photo n'a pas été téléchargée → Vérifiez les logs FETCH_PHOTOS
- Nginx ne sert pas le bon dossier → Vérifiez la config nginx

---

### 8. Vérifier la configuration nginx en production

```bash
# Sur le serveur - Voir quelle config est chargée
docker exec planflan-container-nginx cat /etc/nginx/conf.d/default.conf | grep -A5 "location /static/uploads"
```

**Attendu :**
```nginx
location /static/uploads/ {
    alias /var/www/uploads/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

**Si la configuration est différente ou manquante :**
→ Le fichier `nginx/default.conf` n'est pas correctement monté ou est obsolète.

---

### 9. Vérifier le niveau de logs

Le niveau de logs en production est `WARNING` par défaut, ce qui peut masquer les logs `INFO` de FETCH_PHOTOS.

**Solution temporaire - Augmenter le niveau de logs :**

```bash
# Sur le serveur - Éditer app/configprod.py
# Changer LOG_LEVEL = "WARNING" en LOG_LEVEL = "INFO"
```

Puis redémarrer :
```bash
docker compose restart planflan-backend
```

**Après avoir résolu le problème, remettre à WARNING.**

---

### 10. Tester la connexion API Google depuis le conteneur

```bash
# Sur le serveur - Tester l'accès à l'API Google Places
docker exec planflan-container-backend curl -s "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=photos&key=VOTRE_CLE_API" | head -50
```

**Attendu :** Une réponse JSON avec des photos.

**Si erreur réseau :**
→ Le serveur ou le conteneur bloque les connexions sortantes vers Google. Vérifiez le pare-feu.

---

## 🚀 Actions correctives selon le diagnostic

### Cas 1 : Problème de clé API Google
```bash
# Sur le serveur - Éditer .env avec la bonne clé
nano /path/to/.env
# Puis redémarrer
docker compose restart planflan-backend
```

### Cas 2 : Problème de permissions sur le volume
```bash
# Sur le serveur
docker exec planflan-container-backend chmod -R 777 /app/static/uploads
```

### Cas 3 : Volume non monté correctement
```bash
# Sur le serveur - Vérifier docker-compose.yml
grep -A2 "photos_volume" docker-compose.yml

# Si le volume n'est pas monté, l'ajouter et redémarrer
docker compose down
docker compose up -d
```

### Cas 4 : Configuration nginx obsolète
```bash
# Sur le serveur - Vérifier que nginx/default.conf contient la section uploads
# Puis redémarrer nginx
docker compose restart nginx
```

### Cas 5 : Les photos sont téléchargées mais pas affichées
→ Problème d'affichage côté frontend. Vérifiez :
1. La base de données contient bien les photos : `SELECT * FROM photos;`
2. Les templates utilisent le bon chemin : `/static/uploads/`
3. Le navigateur ne bloque pas les images (console F12)

---

## 📊 Script de diagnostic automatique

Utilisez le script `diagnostic_photos_prod.sh` **sur le serveur de production** :

```bash
# Copier le script sur le serveur (depuis votre machine locale)
scp diagnostic_photos_prod.sh user@serveur:/path/to/planflan2/

# Sur le serveur
cd /path/to/planflan2
chmod +x diagnostic_photos_prod.sh
./diagnostic_photos_prod.sh
```

---

## 🔄 Différences clés Local vs Production

| Aspect | Docker Local | Production |
|--------|--------------|------------|
| **Port HTTP** | 81 | 80 |
| **HTTPS** | Non | Oui (443) |
| **Config nginx** | default.dev.conf | default.conf |
| **FLASK_CONFIG** | Config (dev) | ConfigProd |
| **LOG_LEVEL** | DEBUG | WARNING |
| **Certificats SSL** | Non | Oui (Let's Encrypt) |

**Le problème le plus probable :** Restrictions de la clé API Google en production (domaine HTTPS vs local HTTP).

---

## 📝 Checklist finale

- [ ] Clé API Google vérifiée dans Google Cloud Console
- [ ] Restrictions API levées pour `planflan.fr`
- [ ] Logs FETCH_PHOTOS examinés
- [ ] Dossier `/app/static/uploads` accessible en écriture
- [ ] Volume `photos_volume` monté dans backend ET nginx
- [ ] Configuration nginx contient `location /static/uploads/`
- [ ] Test d'accès HTTPS à une photo réussi
- [ ] Base de données contient des enregistrements dans la table `photos`

---

## 💡 Astuce pour déboguer en temps réel

Suivez les logs en direct pendant que vous ajoutez un établissement :

```bash
# Sur le serveur - Terminal 1
docker logs -f planflan-container-backend

# Sur le serveur - Terminal 2
# Ajoutez un établissement via l'interface web
```

Vous verrez immédiatement les logs FETCH_PHOTOS et pourrez identifier l'erreur.
