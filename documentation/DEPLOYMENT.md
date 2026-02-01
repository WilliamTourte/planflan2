# Déploiement de l'application Flask en production

Ce guide explique comment déployer l'application Flask en production.

## Prérequis

- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)
- MySQL (ou autre base de données compatible)
- Un serveur Linux (recommandé pour la production)

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/planflan2.git
cd planflan2
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Linux/Mac
# .venv\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copier le fichier `.env.example` en `.env` et modifier les valeurs :

```bash
cp .env.example .env
nano .env
```

## Configuration

### Fichiers de configuration

- `.env` : Variables d'environnement
- `gunicorn_config.py` : Configuration de Gunicorn
- `wsgi.py` : Point d'entrée WSGI
- `config_prod.py` : Configuration de l'application

### Configuration de la base de données

Modifier le fichier `.env` pour configurer la connexion à la base de données :

```
DATABASE_URL=mysql+pymysql://utilisateur:motdepasse@localhost/nom_base_de_donnees
```

## Démarrage de l'application

### En développement

```bash
flask run
```

### En production avec Gunicorn

```bash
./run_production.sh
```

Ou directement :

```bash
gunicorn --config gunicorn_config.py wsgi:app
```

### En production avec Waitress (alternative)

```bash
waitress-serve --host=0.0.0.0 --port=8000 wsgi:app
```

## Déploiement avec Docker (optionnel)

### 1. Créer un Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
```

### 2. Construire l'image Docker

```bash
docker build -t planflan2 .
```

### 3. Démarrer le conteneur

```bash
docker run -d -p 8000:8000 --env-file .env planflan2
```

## Déploiement avec Nginx (recommandé)

### 1. Installer Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Configurer Nginx

Créer un fichier de configuration dans `/etc/nginx/sites-available/planflan2` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /chemin/vers/votre/app/app/static/;
        expires 30d;
    }
}
```

### 3. Activer la configuration

```bash
sudo ln -s /etc/nginx/sites-available/planflan2 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Configurer un service systemd

Créer un fichier `/etc/systemd/system/planflan2.service` :

```ini
[Unit]
Description=PlanFlan2 Flask Application
After=network.target

[Service]
User=votre-utilisateur
Group=www-data
WorkingDirectory=/chemin/vers/votre/app
Environment="PATH=/chemin/vers/votre/app/.venv/bin"
ExecStart=/chemin/vers/votre/app/.venv/bin/gunicorn --config gunicorn_config.py wsgi:app

[Install]
WantedBy=multi-user.target
```

### 5. Démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl start planflan2
sudo systemctl enable planflan2
```

## Sécurité

### 1. Configurer HTTPS avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

### 2. Configurer un pare-feu

```bash
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
```

## Maintenance

### Mettre à jour l'application

```bash
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart planflan2
```

### Voir les logs

```bash
# Logs de l'application
journalctl -u planflan2 -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

## Résolution des problèmes

### Problème : L'application ne démarre pas

- Vérifier les logs : `journalctl -u planflan2 -f`
- Vérifier la configuration de la base de données
- Vérifier les permissions des fichiers

### Problème : Erreur 502 Bad Gateway

- Vérifier que Gunicorn est en cours d'exécution
- Vérifier la configuration de Nginx
- Vérifier que le port 8000 est accessible

### Problème : Erreur de connexion à la base de données

- Vérifier les informations de connexion dans `.env`
- Vérifier que le serveur MySQL est en cours d'exécution
- Vérifier que l'utilisateur a les permissions nécessaires

## Bonnes pratiques

1. **Sauvegardes régulières** : Sauvegardez votre base de données régulièrement
2. **Mises à jour** : Mettez à jour régulièrement les dépendances
3. **Monitoring** : Configurez un système de monitoring (ex: Prometheus, Grafana)
4. **Logs** : Configurez une rotation des logs pour éviter de remplir le disque
5. **Sécurité** : Mettez à jour régulièrement le système et les dépendances


2. Reconstruire l'image Docker :
Exécutez les commandes suivantes pour reconstruire l'image Docker :
docker compose down
docker compose build --no-cache
docker compose up -d

3. Vérifier que l'application fonctionne :
Après avoir reconstruit l'image Docker, vérifier que l'application fonctionne correctement :
docker logs planflan-container-backend

# Suite à changement dans l'application
docker compose up -d --no-deps --build planflan-backend 

# Pour recréer la base de données
docker exec -it planflan-container-backend python scripts/recrer_db.py

# Pour restaurer une sauvegarde sur le Docker
docker exec -i planflan-container-db mysql -u root -p < /home/enkyl/planflan2/docker-db/db/backups/planflan_db-XXXXXXXXX.sql