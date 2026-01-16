# Guide de Backup et Restore Automatique pour PlanFlan

Ce guide explique comment utiliser les scripts de backup et restore pour sauvegarder et restaurer à la fois la base de données MySQL et les photos de votre application PlanFlan.

## Structure des fichiers

```
.
├── backup_and_restore_db.sh          # Script existant pour la base de données
├── backup_photos.sh                 # Script existant pour les photos (basique)
├── backup_photos_complete.sh        # Nouveau script complet pour les photos
├── setup_photos_backup_cron.sh      # Script pour configurer les sauvegardes automatiques
├── backup_and_restore_complete.sh   # Script unifié pour tout sauvegarder/restaurer
└── backups/
    ├── photos/                      # Sauvegardes des photos
    └── *.sql                        # Sauvegardes de la base de données
```

## Prérequis

1. Docker et Docker Compose installés
2. Les conteneurs PlanFlan en cours d'exécution
3. Droits d'exécution sur les scripts

## Configuration

### 1. Rendre les scripts exécutables

```bash
chmod +x backup_photos_complete.sh
chmod +x setup_photos_backup_cron.sh
chmod +x backup_and_restore_complete.sh
```

### 2. Adapter les scripts à votre configuration

Modifiez les variables au début de chaque script pour correspondre à votre configuration :

- `CONTAINER_NAME` : Nom de votre conteneur backend (par défaut : `planflan-container-backend`)
- `PHOTOS_VOLUME_NAME` : Nom du volume Docker pour les photos (par défaut : `photos_volume`)
- `BACKUP_DIR` : Répertoire où stocker les sauvegardes
- `MAX_BACKUPS` : Nombre maximum de sauvegardes à conserver
- `CRON_SCHEDULE` : Planification des sauvegardes automatiques

## Utilisation

### Sauvegarde manuelle

#### Sauvegarder uniquement les photos

```bash
./backup_photos_complete.sh backup
```

#### Sauvegarder uniquement la base de données

```bash
./backup_and_restore_db.sh backup
```

#### Sauvegarder à la fois la base de données et les photos

```bash
./backup_and_restore_complete.sh backup
```

### Restauration manuelle

#### Restaurer uniquement les photos (dernière sauvegarde)

```bash
./backup_photos_complete.sh restore
```

#### Restaurer une sauvegarde spécifique des photos

```bash
./backup_photos_complete.sh restore backups/photos/photos_backup_20231201_120000.tar.gz
```

#### Restaurer uniquement la base de données

```bash
./backup_and_restore_db.sh restore
```

#### Restaurer à la fois la base de données et les photos

```bash
./backup_and_restore_complete.sh restore
```

### Gestion des sauvegardes

#### Lister les sauvegardes disponibles

```bash
./backup_photos_complete.sh list
./backup_and_restore_complete.sh list
```

#### Configurer les sauvegardes automatiques

```bash
./setup_photos_backup_cron.sh add
```

#### Supprimer les sauvegardes automatiques

```bash
./setup_photos_backup_cron.sh remove
```

#### Tester une sauvegarde manuellement

```bash
./setup_photos_backup_cron.sh test
```

## Sauvegardes automatiques avec Cron

### Configuration

Le script `setup_photos_backup_cron.sh` permet de configurer des sauvegardes automatiques des photos :

```bash
# Ajouter une tâche cron pour les sauvegardes automatiques
./setup_photos_backup_cron.sh add

# Supprimer la tâche cron
./setup_photos_backup_cron.sh remove

# Lister les tâches cron
./setup_photos_backup_cron.sh list

# Tester la sauvegarde
./setup_photos_backup_cron.sh test
```

### Planification par défaut

- **Fréquence** : Tous les jours à 2h du matin (`0 2 * * *`)
- **Log** : `backups/photos/backup_photos.log`

### Personnalisation

Pour modifier la fréquence des sauvegardes, éditez le script `setup_photos_backup_cron.sh` et changez la variable `CRON_SCHEDULE` :

```bash
# Exemples de planification cron
CRON_SCHEDULE="0 2 * * *"    # Tous les jours à 2h
CRON_SCHEDULE="0 2 * * 0"    # Tous les dimanches à 2h
CRON_SCHEDULE="0 */6 * * *"   # Toutes les 6 heures
CRON_SCHEDULE="0 2 1 * *"    # Le 1er de chaque mois à 2h
```

## Restauration complète

Pour une restauration complète (base de données + photos) :

1. **Arrêter les conteneurs** (si nécessaire) :
   ```bash
   docker-compose down
   ```

2. **Démarrer les conteneurs** :
   ```bash
   docker-compose up -d
   ```

3. **Restaurer les données** :
   ```bash
   ./backup_and_restore_complete.sh restore
   ```

## Bonnes pratiques

1. **Testez vos sauvegardes** : Effectuez régulièrement des tests de restauration pour vous assurer que vos sauvegardes fonctionnent.

2. **Stockage externe** : Envisagez de copier vos sauvegardes vers un stockage externe (cloud, autre serveur) pour une protection supplémentaire.

3. **Rotation des sauvegardes** : Le système conserve par défaut les 5 dernières sauvegardes. Ajustez `MAX_BACKUPS` selon vos besoins.

4. **Surveillance** : Vérifiez régulièrement les logs des sauvegardes automatiques.

5. **Sécurité** : Protégez vos sauvegardes avec des permissions appropriées :
   ```bash
   chmod 700 backups/
   chmod 600 backups/photos/*
   ```

## Dépannage

### Problèmes courants

1. **Permission refusée** :
   ```bash
   chmod +x backup_*.sh
   sudo ./backup_photos_complete.sh backup
   ```

2. **Conteneur non trouvé** :
   ```bash
   docker-compose up -d
   docker ps  # Vérifier que les conteneurs sont en cours d'exécution
   ```

3. **Volume Docker introuvable** :
   ```bash
   docker volume ls  # Vérifier que le volume existe
   docker volume inspect photos_volume
   ```

4. **Espace disque insuffisant** :
   ```bash
   df -h  # Vérifier l'espace disque
   du -sh backups/  # Vérifier la taille des sauvegardes
   ```

### Vérification des logs

Pour les sauvegardes automatiques :
```bash
tail -f backups/photos/backup_photos.log
```

Pour les erreurs Docker :
```bash
docker logs planflan-container-backend
```

## Intégration avec votre workflow existant

### Avant un redémarrage des conteneurs

```bash
# Sauvegarder avant de redémarrer
docker-compose down
docker-compose up -d
```

### Après un déploiement

```bash
# Sauvegarder après un déploiement réussi
./backup_and_restore_complete.sh backup
```

### Dans un script de déploiement

```bash
#!/bin/bash

# Sauvegarder avant le déploiement
./backup_and_restore_complete.sh backup

if [ $? -ne 0 ]; then
    echo "Échec de la sauvegarde, annulation du déploiement"
    exit 1
fi

# Effectuer le déploiement
docker-compose down
docker-compose up -d

# Vérifier que tout fonctionne
if [ $? -eq 0 ]; then
    echo "Déploiement réussi"
else
    echo "Échec du déploiement, restauration..."
    ./backup_and_restore_complete.sh restore
fi
```

## Sécurité des sauvegardes

Pour sécuriser vos sauvegardes, vous pouvez :

1. **Chiffrer les sauvegardes** :
   ```bash
   # Chiffrer une sauvegarde
gpg -c backups/photos/photos_backup_20231201_120000.tar.gz

   # Déchiffrer une sauvegarde
gpg -d backups/photos/photos_backup_20231201_120000.tar.gz.gpg
   ```

2. **Copier vers un stockage distant** :
   ```bash
   # Utiliser rsync pour copier vers un serveur distant
   rsync -avz backups/ user@backup-server:/chemin/vers/sauvegardes/

   # Utiliser AWS S3
   aws s3 sync backups/ s3://votre-bucket-sauvegardes/
   ```

3. **Configurer des alertes** :
   ```bash
   # Ajouter des notifications par email en cas d'échec
   # Dans votre crontab :
   0 2 * * * /chemin/vers/backup_photos_complete.sh backup >> /chemin/vers/log 2>&1 || echo "Échec de la sauvegarde" | mail -s "Alerte sauvegarde" admin@example.com
   ```

## Conclusion

Ce système de backup et restore automatique vous permet de :

- ✅ Sauvegarder automatiquement vos photos et votre base de données
- ✅ Restaurer facilement en cas de problème
- ✅ Configurer des sauvegardes régulières avec cron
- ✅ Gérer plusieurs versions de sauvegardes
- ✅ Surveiller l'état de vos sauvegardes

N'oubliez pas de tester régulièrement vos procédures de restauration pour vous assurer que tout fonctionne correctement en cas de besoin réel.