#!/bin/bash

# Configurer le renouvellement automatique via cron
(crontab -l 2>/dev/null; echo "0 0,12 * * * $PWD/letsencrypt/renew-certificates.sh >> $PWD/letsencrypt/renew.log 2>&1") | crontab -

echo "Renouvellement automatique configuré pour s'exécuter deux fois par jour."
