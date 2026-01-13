#!/bin/bash

# Script pour configurer la tâche cron pour les sauvegardes automatiques de la base de données

# Chemin vers le script de sauvegarde
BACKUP_SCRIPT="/home/damien/PlanFlan/planflan2/docker-db/backup_db.sh"

# Chemin vers le fichier de log pour les sauvegardes
LOG_FILE="/home/damien/PlanFlan/planflan2/docker-db/backup.log"

# Ajouter la tâche cron pour exécuter le script de sauvegarde tous les jours à 2h du matin
(crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1") | crontab -

echo "Tâche cron configurée pour exécuter le script de sauvegarde tous les jours à 2h du matin."
