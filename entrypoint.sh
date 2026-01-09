#!/bin/sh
# Attendre que MySQL soit joignable
echo "Connection avec root"
echo "Password ${MYSQL_ROOT_PASSWORD}"
until mysql --skip_ssl=true -h planflan-container-db -uroot -p${MYSQL_ROOT_PASSWORD} -e "SELECT 1;" 2>/dev/null; do
  echo "En attente de MySQL..."
  sleep 2
done

echo "Export de la variable FLASK_CONFIG"
# On règle la variable d'environnement FLASK_CONFIG pour la production
export FLASK_CONFIG="ConfigProd"  # Utilise config_prod.py

echo "Connexion DB Ok"
echo "Exéccution de la migration DB"
# appliquer les migrations
flask db init
flask db upgrade
flask db migrate

# Démarrer l'app Flask
# exec flask run --host=0.0.0.0
echo "Démarrage de Gunicorn..."
gunicorn --config gunicorn_config.py wsgi:app

echo "Application démarrée avec succès !"
