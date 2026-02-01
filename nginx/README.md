# Configuration Nginx

Ce dossier contient les fichiers de configuration Nginx pour différents environnements.

## Fichiers

### `default.conf`
Configuration pour la **production** avec :
- Support HTTPS/SSL avec Let's Encrypt
- Certificats SSL configurés
- Redirection HTTP → HTTPS
- Configuration ACME pour le renouvellement des certificats

**Utilisation** : Production uniquement

### `default.dev.conf`
Configuration pour le **développement local** avec :
- HTTP uniquement (port 80 → mappé sur 81 de l'hôte)
- Pas de SSL/HTTPS
- Server name : localhost
- Configuration simplifiée pour le debugging

**Utilisation** : Développement local

## Sélection de la configuration

Le fichier utilisé est contrôlé par `docker-compose.override.yml` :

- **Mode Local** (par défaut) : Utilise `default.dev.conf`
- **Mode Production** : Utilise `default.conf`

Pour basculer entre les modes, utilisez le script `switch-env.sh` à la racine du projet :

```bash
# Afficher le mode actuel
./switch-env.sh status

# Passer en mode production
./switch-env.sh prod

# Revenir en mode local
./switch-env.sh local
```

## Notes importantes

- **Ne modifiez pas** `default.conf` pour le développement local
- **Ne committez jamais** de certificats SSL dans le dépôt Git
- Les deux fichiers montent le même upstream : `planflan_upstream_back` pointant vers `planflan-backend:5000`
