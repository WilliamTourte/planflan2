#!/bin/bash

# Tester l'obtention des certificats en mode dry-run
docker compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --dry-run \
  -d planflan.fr -d www.planflan.fr

echo "Test terminé. Si tout est OK, vous pouvez exécuter obtain-certificates.sh"
