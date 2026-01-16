#!/bin/bash

# Script pour exécuter fetch_all_place_photos.py depuis Docker
# Ce script est conçu pour être exécuté depuis le conteneur Docker

# Vérifier que la clé API est fournie
if [ -z "$1" ]; then
    echo "Usage: $0 <GOOGLE_PLACES_API_KEY>"
    echo "Exemple: $0 AIzaSyD..."
    exit 1
fi

API_KEY="$1"

# Exécuter le script Python
python /python-docker/scripts/fetch_all_place_photos.py "$API_KEY"

exit $?