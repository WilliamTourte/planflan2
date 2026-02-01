# ✅ Correction du problème d'affichage des images

## Problème identifié

Les images des établissements (photos Google Maps) ne s'affichent pas car :

1. **Backend** : Télécharge les images dans `/app/static/uploads/` (volume Docker `photos_volume`)
2. **Nginx** : N'avait PAS accès à ce volume et proxiait les requêtes vers Flask
3. **Flask** : En mode production, ne sert pas les fichiers statiques efficacement

## Modifications effectuées

### 1. docker-compose.yml

Ajout du volume `photos_volume` au conteneur nginx :

```yaml
nginx:
  volumes:
    # ... volumes existants ...
    # Monter le volume des photos pour servir les images statiques
    - photos_volume:/var/www/uploads
```

### 2. nginx/default.dev.conf (Développement local)

Changement de la configuration pour servir les fichiers directement :

```nginx
# Servir les fichiers uploads directement depuis le volume partagé
location /static/uploads/ {
  alias /var/www/uploads/;
  expires 30d;
  add_header Cache-Control "public, immutable";
}
```

**AVANT** : `proxy_pass http://planflan_upstream_back;` (proxiait vers Flask)  
**APRÈS** : `alias /var/www/uploads/;` (sert directement les fichiers)

### 3. nginx/default.conf (Production)

Même modification pour les deux blocs server (HTTP et HTTPS).

## Comment appliquer les changements

```bash
# Arrêter les conteneurs
docker compose down

# Redémarrer avec la nouvelle configuration
docker compose up -d

# Attendre quelques secondes
sleep 5

# Vérifier que les conteneurs sont démarrés
docker compose ps

# Tester l'accès à une image
curl -I http://localhost:81/static/uploads/ChIJ4xutfT5u5kcRaJn2NkiOhPU_photo_0.jpg
```

## Vérification

Si tout fonctionne correctement, vous devriez voir :

```
HTTP/1.1 200 OK
Server: nginx/1.29.4
Content-Type: image/jpeg
Cache-Control: public, immutable
Expires: ...
```

Au lieu de :

```
HTTP/1.1 404 Not Found
```

## Production

**OUI, cela fonctionnera en production** car :

1. ✅ Le volume `photos_volume` est partagé entre backend et nginx
2. ✅ Nginx sert les fichiers directement (plus rapide et plus efficace)
3. ✅ Les en-têtes de cache sont configurés (30 jours)
4. ✅ La configuration est identique pour HTTP (port 80) et HTTPS (port 443)

## Architecture mise à jour

```
┌─────────────────────────────────────┐
│    Client (Navigateur)              │
└─────────────────┬───────────────────┘
                  │
         ┌────────▼────────┐
         │  Nginx          │
         │  Port 81 (dev)  │
         │  Port 80/443    │
         │  (prod)         │
         └────────┬────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    │  /static/uploads/         │  Autres requêtes
    │  (fichiers statiques)     │  (API, pages)
    │                           │
    ▼                           ▼
┌───────────┐         ┌──────────────────┐
│  Volume   │         │  Flask Backend   │
│  photos_  │◄────────┤  Gunicorn        │
│  volume   │ écrit   │  Port 5000       │
│           │         └──────────────────┘
│ /var/www/ │
│ uploads/  │
└───────────┘
```

## Avantages de cette approche

1. **Performance** : Nginx sert les fichiers statiques directement (beaucoup plus rapide)
2. **Scalabilité** : Flask ne gère plus les fichiers statiques
3. **Cache** : Les images sont mises en cache côté client (30 jours)
4. **Production-ready** : Configuration identique en dev et prod

## Notes importantes

- Le volume `photos_volume` est **persistant** : les images ne sont pas supprimées quand les conteneurs redémarrent
- Les images sont accessibles à `/static/uploads/` dans l'URL mais stockées dans `/var/www/uploads/` dans nginx
- En production, assurez-vous que le volume est bien sauvegardé (voir scripts de backup)

## Test après modification

1. Arrêtez et redémarrez Docker Compose
2. Créez un nouvel établissement avec une photo Google Maps
3. Vérifiez que l'image s'affiche dans la carte
4. Ouvrez les outils de développement du navigateur (F12) et vérifiez :
   - L'onglet "Network" montre que l'image charge avec un statut 200
   - L'en-tête "Server" indique "nginx" (et pas Flask/Werkzeug)
   - L'en-tête "Cache-Control" est présent

## Fichiers modifiés

1. `/home/damien/PycharmProjects/planflan2/docker-compose.yml`
2. `/home/damien/PycharmProjects/planflan2/nginx/default.dev.conf`
3. `/home/damien/PycharmProjects/planflan2/nginx/default.conf`
