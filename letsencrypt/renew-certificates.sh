#!/bin/bash

# Renouveler les certificats
docker compose run --rm certbot renew

# Recharger la configuration nginx pour appliquer les nouveaux certificats
docker compose exec nginx nginx -s reload

echo "Renouvellement des certificats terminé."
