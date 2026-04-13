#!/bin/bash

# Arrêter nginx temporairement
docker compose stop nginx

# Attendre que nginx soit complètement arrêté
sleep 10

# Renouveler les certificats en utilisant le serveur intégré de certbot
# Utiliser --standalone pour que certbot gère lui-même le serveur de challenge
docker compose run --rm --service-ports certbot renew --standalone --force-renewal

# Redémarrer nginx avec les nouveaux certificats
docker compose up -d nginx

echo "Renouvellement des certificats terminé."
