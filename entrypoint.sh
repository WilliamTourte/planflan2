#!/bin/sh
# Attendre que MySQL soit joignable
echo "Connection avec root"
echo "Password ${MYSQL_ROOT_PASSWORD}"
until mysql --skip_ssl=true -h planflan-container-db -uroot -p${MYSQL_ROOT_PASSWORD} -e "SELECT 1;" 2>/dev/null; do
  echo "En attente de MySQL..."
  sleep 2
done
# ppliquer les migrations
flask db upgrade
# Démarrer l'app Flask
exec flask run --host=0.0.0.0
