#!/bin/bash

# Script pour sauvegarder les photos avant un docker compose down

# Répertoire source des photos
PHOTOS_DIR="./app/static/uploads"

# Répertoire de sauvegarde des photos
BACKUP_DIR="./backups/photos"

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Nom du fichier de sauvegarde
BACKUP_FILE="photos_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

# Sauvegarder les photos
echo "Sauvegarde des photos..."
tar -czf "$BACKUP_DIR/$BACKUP_FILE" -C "$PHOTOS_DIR" .

if [ $? -eq 0 ]; then
    echo "Sauvegarde des photos réussie : $BACKUP_DIR/$BACKUP_FILE"
else
    echo "Échec de la sauvegarde des photos"
    exit 1
fi
