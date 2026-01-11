#!/bin/bash

# Arrêter nginx temporairement pour permettre à Certbot de répondre aux défis
docker compose stop nginx

# Obtenir les certificats avec Certbot
docker compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email damien.hugonnard@gmail.com --agree-tos --no-eff-email \
  -d planflan.fr -d www.planflan.fr

# Redémarrer nginx avec les nouveaux certificats
docker compose up -d nginx

echo "Certificats obtenus avec succès !"
