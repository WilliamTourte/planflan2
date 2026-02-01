# 🔍 Analyse des différences Local Docker vs Production

## Résumé du problème

**Symptôme :** Les photos Google Places s'affichent correctement en Docker local mais pas en production.

## 🎯 Causes probables (par ordre de probabilité)

### 1. 🔑 Restrictions de la clé API Google Maps (80% de chances)

**Pourquoi c'est probable :**
- En local : `http://localhost:81`
- En production : `https://planflan.fr`

La clé API peut avoir des restrictions par :
- **Domaine/Référent HTTP** : Si configuré pour `localhost` uniquement
- **IP** : Si l'IP du serveur de production n'est pas autorisée
- **API** : Si Places API n'est pas activée pour cette clé

**Comment vérifier :**
1. Console Google Cloud Platform → APIs & Services → Credentials
2. Cliquer sur votre clé API
3. Vérifier les sections :
   - "API restrictions" → Places API doit être incluse
   - "Application restrictions" → 
     - Option "None" (recommandé pour tester)
     - OU "HTTP referrers" avec `planflan.fr/*` et `*.planflan.fr/*`
     - OU "IP addresses" avec l'IP de votre serveur

**Symptôme dans les logs :**
```
[FETCH_PHOTOS] Aucune photo trouvée dans les détails de l'établissement
```
ou
```
[FETCH_PHOTOS] Erreur API Google: status=403
```

**Solution :**
- Retirer temporairement toutes les restrictions pour tester
- Ou ajouter `planflan.fr` dans les référents autorisés

---

### 2. 📝 Niveau de logs trop élevé (WARNING au lieu de INFO)

**Pourquoi c'est probable :**
- `app/configprod.py` ligne 93 : `LOG_LEVEL = "WARNING"`
- Les logs `[FETCH_PHOTOS]` utilisent `logger.info()`

**Conséquence :** Vous ne voyez PAS les logs de diagnostic, donc impossible de savoir où ça bloque.

**Comment vérifier :**
```bash
docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS
```
Si vide → c'est probablement ça.

**Solution temporaire :**
```python
# Dans app/configprod.py
LOG_LEVEL = "INFO"  # Au lieu de "WARNING"
```

Puis : `docker compose restart planflan-backend`

---

### 3. 🔒 Pare-feu bloquant les appels sortants vers Google

**Pourquoi c'est probable :**
Certains serveurs de production ont des règles de pare-feu strictes.

**Comment vérifier :**
```bash
docker exec planflan-container-backend curl -I https://maps.googleapis.com/
```

Si timeout ou erreur réseau → le pare-feu bloque.

**Solution :**
Autoriser les connexions sortantes vers :
- `maps.googleapis.com` (port 443)
- `*.googleapis.com` (port 443)

---

### 4. 📂 Configuration UPLOAD_FOLDER incorrecte

**Pourquoi c'est moins probable :**
Le code dans `app/configprod.py` utilise un chemin absolu calculé dynamiquement :
```python
UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
)
```

**Mais vérifiez quand même :**
```bash
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    print('UPLOAD_FOLDER:', app.config['UPLOAD_FOLDER'])
    print('Existe:', os.path.exists(app.config['UPLOAD_FOLDER']))
"
```

**Attendu :** `/app/static/uploads` et `True`

---

### 5. 🗂️ Variable d'environnement GOOGLE_MAPS_API_KEY non chargée

**Pourquoi c'est possible :**
Le fichier `.env` n'est peut-être pas au bon endroit en production.

**Comment vérifier :**
```bash
docker exec planflan-container-backend python -c "
import os
os.environ['FLASK_CONFIG'] = 'ConfigProd'
from app import create_app
app = create_app()
with app.app_context():
    key = app.config.get('GOOGLE_MAPS_API_KEY')
    if key:
        print(f'Clé chargée: {key[:10]}...')
    else:
        print('✗ Clé non chargée !')
"
```

**Solution si vide :**
```bash
# Vérifier que .env est dans le bon dossier
docker exec planflan-container-backend cat /app/.env | grep GOOGLE_MAPS_API_KEY
```

---

### 6. 🌐 Configuration nginx différente

**Pourquoi c'est peu probable :**
Le fichier `nginx/default.conf` contient bien la section pour servir les uploads.

**Mais vérifiez :**
```bash
docker exec planflan-container-nginx cat /etc/nginx/conf.d/default.conf | grep -A5 "/static/uploads"
```

**Attendu :**
```nginx
location /static/uploads/ {
    alias /var/www/uploads/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

**Si absent ou différent :**
```bash
# Vérifier quel fichier est monté
docker compose config | grep -A10 "nginx:" | grep "volumes"
```

---

### 7. 🔐 Différence de protocole HTTP vs HTTPS

**Pourquoi c'est possible :**
L'API Google Places peut se comporter différemment selon :
- Le protocole (HTTP en local, HTTPS en prod)
- Les en-têtes de la requête

**Comment vérifier :**
Comparez les requêtes :
```python
# Code dans app/outils.py ligne 240-246
url = "https://maps.googleapis.com/maps/api/place/photo"
params = {
    "maxwidth": max_width,
    "photoreference": photo_reference,
    "key": api_key,
}
response = requests.get(url, params=params, stream=True)
```

C'est une requête backend, donc le protocole du site (HTTP/HTTPS) ne devrait pas avoir d'impact.

---

## 🎬 Plan d'action recommandé

### Étape 1 : Activer les logs détaillés
```bash
# Sur le serveur de production
cd /path/to/planflan2
nano app/configprod.py
# Changer LOG_LEVEL = "WARNING" en LOG_LEVEL = "INFO"
docker compose restart planflan-backend
```

### Étape 2 : Ajouter un établissement et surveiller les logs
```bash
# Terminal 1
docker logs -f planflan-container-backend | grep FETCH_PHOTOS

# Terminal 2 (ou navigateur)
# Créer un établissement avec google_place_id
```

### Étape 3 : Analyser les logs
Selon ce que vous voyez, référez-vous aux causes ci-dessus.

### Étape 4 : Vérifier la clé API
Si les logs montrent "Aucune photo" ou "status=403" :
→ Console Google Cloud → Retirer les restrictions

### Étape 5 : Tester manuellement l'API
```bash
docker exec planflan-container-backend curl -s \
"https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=photos&key=VOTRE_CLE" \
| python -m json.tool
```

---

## 📊 Tableau comparatif des configurations

| Configuration | Docker Local | Production | Impact |
|--------------|--------------|------------|--------|
| **Fichier override** | ✅ docker-compose.override.yml | ❌ Absent | Ports, SSL |
| **Port HTTP** | 81 | 80 | Aucun sur les photos |
| **HTTPS** | ❌ | ✅ | Possible impact clé API |
| **Config nginx** | default.dev.conf | default.conf | Identique pour uploads |
| **FLASK_CONFIG** | Config (implicite) | ConfigProd | LOG_LEVEL différent |
| **LOG_LEVEL** | DEBUG | WARNING | ⚠️ Logs masqués |
| **UPLOAD_FOLDER** | app/static/uploads | /app/static/uploads | Absolu en prod |
| **Volume photos** | ✅ Monté | ✅ Monté | Doit être identique |
| **Permissions uploads** | 777 | 777 | Doit être identique |

---

## 🔎 Code pertinent à examiner

### app/outils.py - fetch_place_photos (lignes 174-292)
Points clés :
- Ligne 207 : Appel `get_place_details(place_id, api_key)`
- Ligne 209 : Si `place_details` est None → pas de photos
- Ligne 233 : Vérification permissions d'écriture
- Ligne 252 : Appel API photo avec `requests.get()`
- Ligne 255 : Vérification `status_code == 200`

### app/configprod.py
- Ligne 61 : `GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")`
- Ligne 93 : `LOG_LEVEL = "WARNING"` ⚠️ **À changer temporairement**

### nginx/default.conf
- Lignes 33-37 : Bloc HTTP
- Lignes 63-67 : Bloc HTTPS
Les deux ont la même config pour `/static/uploads/`

---

## ✅ Checklist de vérification

```bash
# 1. Logs visibles ?
docker logs planflan-container-backend 2>&1 | grep FETCH_PHOTOS | wc -l
# Si 0 → Changer LOG_LEVEL à INFO

# 2. Clé API définie ?
docker exec planflan-container-backend env | grep GOOGLE_MAPS_API_KEY
# Doit afficher la clé

# 3. Dossier uploads accessible ?
docker exec planflan-container-backend ls -la /app/static/uploads/
# Doit être drwxrwxrwx

# 4. API Google accessible ?
docker exec planflan-container-backend curl -I https://maps.googleapis.com/
# Doit retourner HTTP 200 ou 301

# 5. Photos dans la base ?
docker exec planflan-container-db mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT COUNT(*) FROM photos;"
# Si 0 → Les photos ne sont jamais téléchargées

# 6. Photos accessibles via HTTP ?
curl -I https://planflan.fr/static/uploads/defaut_etab.jpg
# Doit retourner 200 (test avec photo par défaut)
```

---

## 💡 Recommandation finale

**Le problème est très probablement lié aux restrictions de la clé API Google.**

**Action immédiate :**
1. Aller sur https://console.cloud.google.com/apis/credentials
2. Cliquer sur votre clé API
3. Retirer TOUTES les restrictions temporairement
4. Sauvegarder
5. Attendre 1-2 minutes (propagation)
6. Tester à nouveau

Si ça fonctionne → c'était bien les restrictions. Vous pourrez ensuite ajouter uniquement `planflan.fr/*` comme référent autorisé.

Si ça ne fonctionne toujours pas → Activez les logs INFO et partagez la sortie de FETCH_PHOTOS.
