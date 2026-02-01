#!/bin/bash

# Script complet pour sauvegarder et restaurer à la fois la base de données et les photos
# Ce script utilise les scripts spécialisés pour chaque composant

# Configuration
DB_BACKUP_SCRIPT="./backup_and_restore_db.sh"
PHOTOS_BACKUP_SCRIPT="./backup_photos_complete.sh"
BACKUP_DIR="./backups"

# Créer le répertoire de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Fonction pour sauvegarder tout
backup_all() {
    echo "=== Début de la sauvegarde complète ==="
    
    # Sauvegarder la base de données
    echo ""
    echo "📁 Sauvegarde de la base de données..."
    bash "$DB_BACKUP_SCRIPT" backup
    
    if [ $? -ne 0 ]; then
        echo "❌ Échec de la sauvegarde de la base de données"
        return 1
    fi
    
    # Sauvegarder les photos
    echo ""
    echo "🖼️  Sauvegarde des photos..."
    bash "$PHOTOS_BACKUP_SCRIPT" backup
    
    if [ $? -ne 0 ]; then
        echo "❌ Échec de la sauvegarde des photos"
        return 1
    fi
    
    echo ""
    echo "✅ Sauvegarde complète réussie"
    return 0
}

# Fonction pour restaurer tout
restore_all() {
    echo "=== Début de la restauration complète ==="
    
    # Vérifier que les conteneurs sont en cours d'exécution
    if ! docker ps | grep -q "planflan-container-backend"; then
        echo "❌ Les conteneurs ne sont pas en cours d'exécution"
        echo "Veuillez démarrer les conteneurs avec 'docker-compose up -d'"
        return 1
    fi
    
    # Restaurer la base de données
    echo ""
    echo "📁 Restauration de la base de données..."
    bash "$DB_BACKUP_SCRIPT" restore
    
    if [ $? -ne 0 ]; then
        echo "❌ Échec de la restauration de la base de données"
        return 1
    fi
    
    # Restaurer les photos
    echo ""
    echo "🖼️  Restauration des photos..."
    bash "$PHOTOS_BACKUP_SCRIPT" restore
    
    if [ $? -ne 0 ]; then
        echo "❌ Échec de la restauration des photos"
        return 1
    fi
    
    echo ""
    echo "✅ Restauration complète réussie"
    return 0
}

# Fonction pour lister toutes les sauvegardes
list_all_backups() {
    echo "=== Liste de toutes les sauvegardes ==="
    
    echo ""
    echo "📁 Sauvegardes de la base de données :"
    ls -lt "./backups/"*.sql 2>/dev/null | head -n 5
    
    echo ""
    echo "🖼️  Sauvegardes des photos :"
    ls -lt "./backups/photos/"*.tar.gz 2>/dev/null | head -n 5
}

# Fonction pour configurer les sauvegardes automatiques
setup_auto_backup() {
    echo "=== Configuration des sauvegardes automatiques ==="
    
    # Configurer la sauvegarde automatique de la base de données
    echo ""
    echo "📁 Configuration de la sauvegarde automatique de la base de données..."
    # Vous devrez adapter cette partie selon votre script existant
    
    # Configurer la sauvegarde automatique des photos
    echo ""
    echo "🖼️  Configuration de la sauvegarde automatique des photos..."
    bash "./setup_photos_backup_cron.sh" add
    
    echo ""
    echo "✅ Configuration des sauvegardes automatiques terminée"
}

# Afficher l'aide
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options :"
    echo "  backup           Sauvegarder la base de données et les photos"
    echo "  restore          Restaurer la base de données et les photos"
    echo "  list             Lister toutes les sauvegardes disponibles"
    echo "  auto-setup       Configurer les sauvegardes automatiques"
    echo "  help             Afficher cette aide"
    echo ""
    echo "Exemples :"
    echo "  $0 backup           # Sauvegarder tout"
    echo "  $0 restore          # Restaurer tout"
    echo "  $0 list             # Lister les sauvegardes"
    echo "  $0 auto-setup       # Configurer les sauvegardes automatiques"
}

# Gestion des arguments
case "$1" in
    backup)
        backup_all
        exit $?
        ;;
    restore)
        restore_all
        exit $?
        ;;
    list)
        list_all_backups
        exit $?
        ;;
    auto-setup)
        setup_auto_backup
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