# Planflan

## Mise en place d'un environnement virtuel Python

1. Création de l'environnement :
```sh
python -m venv env
```
2. Activer l'environnement :
```sh
source env/bin/activate  # ou env\Scripts\activate sur Windows
```

## Gestion des dépendances

1. Installation des dépendances à partir d'un fichier `requirements.txt` existant :
```sh
pip install -r requirements.txt
```

Il est possible de mettre à jour le fichier `requirements.txt` :
```sh
pip freeze > requirements.txt
```

## Mise en place BDD conteneurisée

Dans le dossier `db` est contenu un fichier de configuration `docker-compose.yml` permettant de mettre en place une base de données MariadDB.

Procédure :
1. Installer Docker
2. Dans un terminal, se positionner dans le dossier `db` 
3. Lancer la commande `docker compose up`

La base de données est accessible sur `localhost` via le port `9806`.

PhpMyAdmin est accessible sur `localhost` via le port `8080`.

### Initiasation de la structure des tables

Un script nommé `recrer_db.py` est dipsonible dans le module `app`.

Pour le lancer en ligne de commande :
```sh
python -m app.recrer_db.py
```

## Démarrer le projet en environnement de développment

Une fois l'environnement virutel Python et la base de données fonctionnel vous pourrez lancer le projet en environnement de développement avec la commande suivante :
```sh
flask run
```
