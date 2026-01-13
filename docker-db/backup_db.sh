#!/bin/bash

# Charger les variables d'environnement depuis le fichier .env à la racine
set -a
source /home/damien/PlanFlan/planflan2/.env
set +a

# Nom du conteneur Docker de la base de données
CONTAINER_NAME="mysql-db"

# Nom de la base de données
DB_NAME="$MYSQL_DATABASE"

# Nom d'utilisateur de la base de données
DB_USER="$MYSQL_USER"

# Mot de passe de la base de données
DB_PASSWORD="$MYSQL_PASSWORD"

# Emplacement de sauvegarde
BACKUP_DIR="./db/backups"

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Exécuter la sauvegarde avec mysqldump
docker exec -t "$CONTAINER_NAME" mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_DIR/$DB_NAME-$(date +%Y%m%d-%H%M%S).sql"

# Vérifier si la sauvegarde a réussi
if [ $? -eq 0 ]; then
    echo "Sauvegarde réussie : $BACKUP_DIR/$DB_NAME-$(date +%Y%m%d-%H%M%S).sql"
else
    echo "Échec de la sauvegarde"
fi