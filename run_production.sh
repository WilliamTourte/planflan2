#!/bin/bash

# Script pour démarrer l'application Flask en production

echo "🚀 Démarrage de l'application Flask en production..."

# Activer l'environnement virtuel
if [ -d ".venv" ]; then
    echo "✅ Activation de l'environnement virtuel..."
    source .venv/bin/activate
fi

# Vérifier que les dépendances sont installées
if ! command -v gunicorn &> /dev/null; then
    echo "⚠️  gunicorn n'est pas installé. Installation..."
    pip install gunicorn
fi

# Démarrer l'application avec Gunicorn
echo "🎯 Démarrage de Gunicorn..."
gunicorn --config gunicorn_config.py wsgi:app

echo "✅ Application démarrée avec succès !"
