#!/bin/bash

# Script pour configurer les sauvegardes automatiques des photos avec cron
# Ce script configure un cron job pour exécuter régulièrement les sauvegardes

# Configuration
CRON_SCHEDULE="0 2 * * *"  # Tous les jours à 2h du matin
BACKUP_SCRIPT_PATH="$(pwd)/backup_photos_complete.sh"
LOG_FILE="$(pwd)/backups/photos/backup_photos.log"

# Créer le répertoire de logs s'il n'existe pas
mkdir -p "$(dirname "$LOG_FILE")"

# Vérifier que le script de backup existe
touch "$BACKUP_SCRIPT_PATH"

# Fonction pour ajouter la tâche cron
add_cron_job() {
    echo "Configuration de la tâche cron pour les sauvegardes automatiques des photos..."
    
    # Ajouter la tâche cron
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $BACKUP_SCRIPT_PATH backup >> $LOG_FILE 2>&1") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Tâche cron ajoutée avec succès"
        echo "Planification : $CRON_SCHEDULE"
        echo "Script : $BACKUP_SCRIPT_PATH backup"
        echo "Log : $LOG_FILE"
    else
        echo "❌ Échec de l'ajout de la tâche cron"
        return 1
    fi
}

# Fonction pour supprimer la tâche cron
remove_cron_job() {
    echo "Suppression de la tâche cron pour les sauvegardes des photos..."
    
    # Supprimer la tâche cron spécifique
    crontab -l | grep -v "$BACKUP_SCRIPT_PATH" | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Tâche cron supprimée avec succès"
    else
        echo "❌ Échec de la suppression de la tâche cron"
        return 1
    fi
}

# Fonction pour lister les tâches cron
list_cron_jobs() {
    echo "Tâches cron actuelles :"
    crontab -l
}

# Fonction pour tester la sauvegarde
test_backup() {
    echo "Test de la sauvegarde des photos..."
    
    # Exécuter le script de backup
    bash "$BACKUP_SCRIPT_PATH" backup
    
    if [ $? -eq 0 ]; then
        echo "✅ Test de sauvegarde réussi"
    else
        echo "❌ Échec du test de sauvegarde"
        return 1
    fi
}

# Afficher l'aide
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options :"
    echo "  add      Ajouter la tâche cron pour les sauvegardes automatiques"
    echo "  remove   Supprimer la tâche cron"
    echo "  list     Lister les tâches cron actuelles"
    echo "  test     Tester la sauvegarde manuellement"
    echo "  help     Afficher cette aide"
    echo ""
    echo "Exemples :"
    echo "  $0 add      # Ajouter la tâche cron"
    echo "  $0 remove   # Supprimer la tâche cron"
    echo "  $0 test     # Tester la sauvegarde"
}

# Gestion des arguments
case "$1" in
    add)
        add_cron_job
        exit $?
        ;;
    remove)
        remove_cron_job
        exit $?
        ;;
    list)
        list_cron_jobs
        exit $?
        ;;
    test)
        test_backup
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