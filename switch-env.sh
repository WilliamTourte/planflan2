#!/bin/bash

# Script pour basculer entre les environnements local et production

set -e

OVERRIDE_FILE="docker-compose.override.yml"
BACKUP_FILE="docker-compose.override.yml.bak"

case "$1" in
    local)
        echo "Activation du mode DÉVELOPPEMENT LOCAL..."
        if [ -f "$BACKUP_FILE" ]; then
            mv "$BACKUP_FILE" "$OVERRIDE_FILE"
            echo "✓ Configuration locale activée"
        else
            echo "✓ Configuration locale déjà active"
        fi
        echo ""
        echo "Pour démarrer l'environnement :"
        echo "  docker compose up -d"
        echo ""
        echo "Application accessible sur : http://localhost:81"
        ;;

    prod)
        echo "Activation du mode PRODUCTION..."
        if [ -f "$OVERRIDE_FILE" ]; then
            mv "$OVERRIDE_FILE" "$BACKUP_FILE"
            echo "✓ Configuration de production activée"
        else
            echo "✓ Configuration de production déjà active"
        fi
        echo ""
        echo "Pour démarrer l'environnement :"
        echo "  docker compose up -d"
        echo ""
        echo "Note : Les certificats SSL doivent être configurés pour la production"
        ;;

    status)
        if [ -f "$OVERRIDE_FILE" ]; then
            echo "Mode actuel : DÉVELOPPEMENT LOCAL"
            echo "  - Port HTTP : 81"
            echo "  - SSL : désactivé"
            echo "  - Base de données : port 3307"
        else
            echo "Mode actuel : PRODUCTION"
            echo "  - Port HTTP : 80"
            echo "  - Port HTTPS : 443"
            echo "  - Base de données : port 3306"
        fi
        ;;

    *)
        echo "Usage: $0 {local|prod|status}"
        echo ""
        echo "Commandes :"
        echo "  local   - Activer le mode développement local (port 81, sans SSL)"
        echo "  prod    - Activer le mode production (ports 80/443, avec SSL)"
        echo "  status  - Afficher le mode actuel"
        exit 1
        ;;
esac
