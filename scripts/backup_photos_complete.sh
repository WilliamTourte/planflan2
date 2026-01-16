#!/bin/bash

# Script complet pour sauvegarder et restaurer les photos avec Docker
# Ce script gère à la fois les sauvegardes et les restaurations des photos
# stockées dans le volume Docker photos_volume

# Configuration
BACKUP_DIR="./backups/photos"            # Répertoire pour stocker les sauvegardes
CONTAINER_NAME="planflan-container-backend"  # Nom du conteneur backend
PHOTOS_VOLUME_NAME="photos_volume"      # Nom du volume Docker pour les photos
MAX_BACKUPS=5                           # Nombre maximum de sauvegardes à conserver

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Fonction pour sauvegarder les photos
backup_photos() {
    echo "=== Début de la sauvegarde des photos ==="
    
    # Créer un nom de fichier avec timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="photos_backup_$TIMESTAMP.tar.gz"
    
    # Vérifier que le conteneur est en cours d'exécution
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "❌ Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
        return 1
    fi
    
    # Créer un conteneur temporaire pour accéder au volume
    TEMP_CONTAINER="temp_photos_backup_$TIMESTAMP"
    docker run --rm --name "$TEMP_CONTAINER" -v "$PHOTOS_VOLUME_NAME":/photos -v "$BACKUP_DIR":/backup alpine tar -czf /backup/$BACKUP_FILE -C /photos .
    
    if [ $? -eq 0 ]; then
        echo "✅ Sauvegarde réussie : $BACKUP_DIR/$BACKUP_FILE"
        
        # Nettoyer les anciennes sauvegardes
        cleanup_old_backups
        
        return 0
    else
        echo "❌ Échec de la sauvegarde des photos"
        return 1
    fi
}

# Fonction pour restaurer les photos
restore_photos() {
    echo "=== Début de la restauration des photos ==="
    
    # Trouver la sauvegarde la plus récente
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/photos_backup_*.tar.gz | head -n 1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ Aucun fichier de sauvegarde trouvé dans $BACKUP_DIR"
        return 1
    fi
    
    echo "📁 Restauration depuis : $LATEST_BACKUP"
    
    # Vérifier que le conteneur est en cours d'exécution
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "❌ Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
        return 1
    fi
    
    # Créer un conteneur temporaire pour restaurer les photos
    TEMP_CONTAINER="temp_photos_restore_$(date +%Y%m%d_%H%M%S)"
    docker run --rm --name "$TEMP_CONTAINER" -v "$PHOTOS_VOLUME_NAME":/photos -v "$BACKUP_DIR":/backup alpine sh -c "
        rm -rf /photos/* && 
        tar -xzf /backup/$(basename "$LATEST_BACKUP") -C /photos
    "
    
    if [ $? -eq 0 ]; then
        echo "✅ Restauration réussie depuis $LATEST_BACKUP"
        return 0
    else
        echo "❌ Échec de la restauration des photos"
        return 1
    fi
}

# Fonction pour nettoyer les anciennes sauvegardes
cleanup_old_backups() {
    echo "🧹 Nettoyage des anciennes sauvegardes..."
    
    # Compter le nombre de sauvegardes
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/photos_backup_*.tar.gz 2>/dev/null | wc -l)
    
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        # Calculer le nombre de sauvegardes à supprimer
        TO_DELETE=$((BACKUP_COUNT - MAX_BACKUPS))
        
        # Supprimer les sauvegardes les plus anciennes
        ls -t "$BACKUP_DIR"/photos_backup_*.tar.gz | tail -n "$TO_DELETE" | while read old_backup; do
            echo "🗑️  Suppression de l'ancienne sauvegarde : $old_backup"
            rm "$old_backup"
        done
    fi
}

# Fonction pour lister les sauvegardes disponibles
list_backups() {
    echo "=== Liste des sauvegardes disponibles ==="
    
    if [ -z "$(ls -A "$BACKUP_DIR")" ]; then
        echo "Aucune sauvegarde disponible"
        return 1
    fi
    
    # Lister les sauvegardes par ordre chronologique inverse
    ls -lt "$BACKUP_DIR"/photos_backup_*.tar.gz | awk '{print $6" "$7" "$8" "$9}' | head -n 10
    
    # Afficher le nombre total de sauvegardes
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/photos_backup_*.tar.gz | wc -l)
    echo ""
    echo "Nombre total de sauvegardes : $BACKUP_COUNT"
}

# Fonction pour restaurer une sauvegarde spécifique
restore_specific_backup() {
    if [ -z "$1" ]; then
        echo "❌ Veuillez spécifier le fichier de sauvegarde à restaurer"
        list_backups
        return 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "❌ Fichier de sauvegarde introuvable : $BACKUP_FILE"
        return 1
    fi
    
    echo "📁 Restauration depuis le fichier spécifique : $BACKUP_FILE"
    
    # Vérifier que le conteneur est en cours d'exécution
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "❌ Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
        return 1
    fi
    
    # Créer un conteneur temporaire pour restaurer les photos
    TEMP_CONTAINER="temp_photos_restore_$(date +%Y%m%d_%H%M%S)"
    docker run --rm --name "$TEMP_CONTAINER" -v "$PHOTOS_VOLUME_NAME":/photos -v "$BACKUP_DIR":/backup alpine sh -c "
        rm -rf /photos/* && 
        tar -xzf /backup/$(basename "$BACKUP_FILE") -C /photos
    "
    
    if [ $? -eq 0 ]; then
        echo "✅ Restauration réussie depuis $BACKUP_FILE"
        return 0
    else
        echo "❌ Échec de la restauration des photos"
        return 1
    fi
}

# Afficher l'aide
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options :"
    echo "  backup           Sauvegarder les photos"
    echo "  restore          Restaurer les photos depuis la dernière sauvegarde"
    echo "  restore <file>   Restaurer les photos depuis une sauvegarde spécifique"
    echo "  list             Lister les sauvegardes disponibles"
    echo "  help             Afficher cette aide"
    echo ""
    echo "Exemples :"
    echo "  $0 backup           # Sauvegarder les photos"
    echo "  $0 restore          # Restaurer depuis la dernière sauvegarde"
    echo "  $0 restore backup_20231201_120000.tar.gz  # Restaurer une sauvegarde spécifique"
    echo "  $0 list             # Lister les sauvegardes disponibles"
}

# Gestion des arguments
case "$1" in
    backup)
        backup_photos
        exit $?
        ;;
    restore)
        if [ -n "$2" ]; then
            restore_specific_backup "$2"
        else
            restore_photos
        fi
        exit $?
        ;;
    list)
        list_backups
        exit $?
        ;;
    help|--help|-h|"")
        show_help
        exit 0
        ;;
    *)
        echo "❌ Option invalide : $1"
        show_help
        exit 1
        ;;
esac