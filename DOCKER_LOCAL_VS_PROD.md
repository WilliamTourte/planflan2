# Configuration Docker - Local vs Production

## 🚀 Démarrage Rapide

### Développement Local (Recommandé)

```bash
# L'environnement local est activé par défaut
docker compose up -d

# Accéder à l'application
http://localhost:81
```

### Basculer entre Local et Production

Utilisez le script `switch-env.sh` pour basculer facilement entre les environnements :

```bash
# Vérifier le mode actuel
./switch-env.sh status

# Passer en mode production
./switch-env.sh prod
docker compose down
docker compose up -d

# Revenir en mode local
./switch-env.sh local
docker compose down
docker compose up -d
```

---

## Développement Local

Le fichier `docker-compose.override.yml` est automatiquement utilisé par Docker Compose et configure l'environnement pour le développement local :

### Caractéristiques :
- **Port HTTP** : 81 (au lieu de 80) pour éviter les conflits
- **Pas de HTTPS** : Configuration Nginx simplifiée sans certificats SSL
- **Base de données** : Port 3307 (au lieu de 3306)
- **Certbot désactivé** : Pas besoin de certificats Let's Encrypt en local
- **Debug activé** : FLASK_ENV=development et FLASK_DEBUG=1

### Utilisation :

```bash
# Démarrer l'environnement local
docker compose up

# Ou en arrière-plan
docker compose up -d

# Accéder à l'application
http://localhost:81

# Arrêter les conteneurs
docker compose down
```

## Production

Pour déployer en production, désactivez le fichier override :

### Option 1 : Utiliser uniquement docker-compose.yml

```bash
# Renommer temporairement le fichier override
mv docker-compose.override.yml docker-compose.override.yml.bak

# Démarrer avec la configuration de production
docker compose up -d

# Restaurer après
mv docker-compose.override.yml.bak docker-compose.override.yml
```

### Option 2 : Utiliser un profil de production

```bash
# Démarrer avec le profil production (inclut certbot)
docker compose --profile production up -d
```

### Option 3 : Fichier override spécifique pour la production

Créez un fichier `docker-compose.prod.yml` et utilisez-le :

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Fichiers de configuration Nginx

- **`nginx/default.conf`** : Configuration de production avec HTTPS et Let's Encrypt
- **`nginx/default.dev.conf`** : Configuration de développement sans SSL (utilisée par override)

## Basculer entre les environnements

### Local → Production
```bash
# Arrêter l'environnement local
docker compose down

# Renommer le fichier override
mv docker-compose.override.yml docker-compose.override.yml.dev

# Démarrer en production
docker compose up -d
```

### Production → Local
```bash
# Arrêter l'environnement de production
docker compose down

# Restaurer le fichier override
mv docker-compose.override.yml.dev docker-compose.override.yml

# Démarrer en local
docker compose up -d
```

## Ports utilisés

| Service | Local | Production |
|---------|-------|------------|
| HTTP    | 81    | 80         |
| HTTPS   | -     | 443        |
| MySQL   | 3307  | 3306       |

## Variables d'environnement

Le fichier override active automatiquement :
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`

En production, ces variables ne sont pas définies, utilisant les valeurs par défaut de production.
