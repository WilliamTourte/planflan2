#!/bin/sh
# Attendre que MySQL soit joignable
echo "Connection avec root"
echo "Password ${MYSQL_ROOT_PASSWORD}"
# Utiliser MYSQL_HOST si défini, sinon utiliser planflan-container-db
MYSQL_HOST=${MYSQL_HOST:-planflan-container-db}
until mysql --skip_ssl=true -h ${MYSQL_HOST} -uroot -p${MYSQL_ROOT_PASSWORD} -e "SELECT 1;" 2>/dev/null; do
  echo "En attente de MySQL..."
  sleep 2
done

echo "Export de la variable FLASK_CONFIG"
# On règle la variable d'environnement FLASK_CONFIG pour la production
export FLASK_CONFIG="ConfigProd"  # Utilise config_prod.py

echo "Connexion DB Ok"
echo "Exécution de la migration DB"
# appliquer les migrations
flask db init

echo "DB migrate"
flask db migrate

echo "DB Upgrade"
flask db upgrade

# Démarrer l'app Flask
# exec flask run --host=0.0.0.0
echo "Démarrage de Gunicorn..."
# python -m wsgi à tester
gunicorn --config gunicorn_config.py wsgi:app

echo "Application démarrée avec succès !"
