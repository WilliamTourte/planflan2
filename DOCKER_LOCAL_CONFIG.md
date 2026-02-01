# Configuration Docker - Développement Local

## Problème résolu : Conflit de port MySQL

### Situation
Votre MySQL local utilise le port `3306`, ce qui crée un conflit avec le conteneur MySQL Docker.

### Solution
Le port MySQL Docker a été mappé sur `3307` au lieu de `3306`.

## Configuration des ports

| Service | Port Local | Port Conteneur | Description |
|---------|------------|----------------|-------------|
| MySQL | **3307** | 3306 | Base de données (évite conflit avec MySQL local) |
| Backend | 5000 | 5000 | Application Flask |
| Nginx HTTP | 80 | 80 | Serveur web |
| Nginx HTTPS | 443 | 443 | Serveur web sécurisé |

## Utilisation

### Démarrer les conteneurs
```bash
docker compose up
# ou en arrière-plan
docker compose up -d
```

### Se connecter à MySQL Docker depuis l'hôte
```bash
# Depuis votre machine locale
mysql -h 127.0.0.1 -P 3307 -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}
```

### Se connecter à MySQL local (inchangé)
```bash
# Votre MySQL local reste sur le port 3306
mysql -h 127.0.0.1 -P 3306 -u root -p
```

### Arrêter les conteneurs
```bash
docker compose down
```

### Voir les logs
```bash
# Tous les conteneurs
docker compose logs -f

# Un conteneur spécifique
docker compose logs -f planflan-backend
docker compose logs -f planflan-service-db
```

## Fichiers de configuration

### docker-compose.yml
Fichier principal pour la production et le développement de base.

### docker-compose.override.yml
Fichier optionnel pour personnaliser la configuration en local.
Ce fichier est automatiquement fusionné avec `docker-compose.yml`.

**Avantages** :
- Peut être ajouté au `.gitignore` pour des configurations personnelles
- Ne modifie pas le fichier principal
- Facilite les configurations spécifiques au développement

## Basculer entre MySQL local et MySQL Docker

### Option 1 : Utiliser MySQL Docker pour développement
```bash
# Dans votre .env ou configuration
DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3307/${MYSQL_DATABASE}
```

### Option 2 : Utiliser MySQL local pour développement
```bash
# Dans votre .env ou configuration
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/planflan_db
```

## Commandes utiles

### Reconstruire les images
```bash
docker compose build --no-cache
```

### Nettoyer tout (attention : supprime les volumes)
```bash
docker compose down -v
```

### Accéder au conteneur backend
```bash
docker exec -it planflan-container-backend bash
```

### Accéder au conteneur MySQL
```bash
docker exec -it planflan-container-db bash
```

### Voir l'état des conteneurs
```bash
docker compose ps
```

### Voir les volumes
```bash
docker volume ls | grep planflan
```

## Troubleshooting

### Port 3307 également occupé
Si le port 3307 est aussi occupé, modifiez dans `docker-compose.yml` :
```yaml
ports:
  - "3308:3306"  # Ou un autre port disponible
```

### Vérifier les ports utilisés
```bash
# Linux
sudo netstat -tlnp | grep -E ':(3306|3307|5000|80|443)'

# Ou avec ss
ss -tlnp | grep -E ':(3306|3307|5000|80|443)'
```

### Conteneur MySQL ne démarre pas
```bash
# Voir les logs détaillés
docker compose logs planflan-service-db

# Vérifier le healthcheck
docker inspect planflan-container-db | grep -A 10 Health
```

### Réinitialiser la base de données Docker
```bash
docker compose down -v  # Supprime les volumes
docker compose up -d    # Recrée tout
```

## Production vs Développement

### En production (serveur)
Le port `3306` n'est généralement pas exposé à l'extérieur du réseau Docker.
Seuls nginx (80/443) et optionnellement l'application (5000) sont exposés.

### En développement (local)
Tous les ports sont exposés pour faciliter le debugging et les tests.

---

**Note** : Ce fichier documente la configuration pour le développement local.
Pour la production, référez-vous à `DEPLOYMENT_PHOTO_FIX.md`.
