#!/bin/bash

# Script pour sauvegarder et restaurer la base de données avant/après docker compose down/up

# Configuration
DB_CONTAINER_NAME="votre_container_db"  # Remplacez par le nom de votre container de base de données
DB_USER="votre_utilisateur"            # Remplacez par votre utilisateur de base de données
DB_PASSWORD="votre_mot_de_passe"      # Remplacez par votre mot de passe de base de données
DB_NAME="votre_base_de_donnees"       # Remplacez par le nom de votre base de données
BACKUP_DIR="./backups"                # Répertoire pour stocker les sauvegardes
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Fonction pour sauvegarder la base de données
backup_db() {
    echo "Sauvegarde de la base de données..."
    docker exec "$DB_CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Sauvegarde réussie : $BACKUP_DIR/$BACKUP_FILE"
    else
        echo "Échec de la sauvegarde"
        exit 1
    fi
}

# Fonction pour restaurer la base de données
restore_db() {
    echo "Restauration de la base de données..."
    
    # Vérifier si un fichier de sauvegarde existe
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql | head -n 1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo "Aucun fichier de sauvegarde trouvé dans $BACKUP_DIR"
        exit 1
    fi
    
    echo "Restauration depuis : $LATEST_BACKUP"
    cat "$LATEST_BACKUP" | docker exec -i "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"
    
    if [ $? -eq 0 ]; then
        echo "Restauration réussie"
    else
        echo "Échec de la restauration"
        exit 1
    fi
}

# Vérifier si le container de base de données est en cours d'exécution
if docker ps | grep -q "$DB_CONTAINER_NAME"; then
    echo "Le container de base de données est en cours d'exécution."
    
    # Sauvegarder la base de données avant le down
    backup_db
    
    # Arrêter les containers
    echo "Arrêt des containers..."
    docker compose down
    
    # Démarrer les containers
    echo "Démarrage des containers..."
    docker compose up -d
    
    # Attendre que le container de base de données soit prêt
    echo "Attente que le container de base de données soit prêt..."
    sleep 10
    
    # Restaurer la base de données après le up
    restore_db
else
    echo "Le container de base de données n'est pas en cours d'exécution."
    exit 1
fi
