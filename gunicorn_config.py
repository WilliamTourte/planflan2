# Configuration pour Gunicorn

# Adresse et port de liaison
bind = "0.0.0.0:5000"

# Nombre de workers (2 * nombre de cœurs + 1)
workers = 5

# Type de worker (sync pour les applications simples)
worker_class = "sync"

# Timeout pour les workers (en secondes)
timeout = 120

# Fichier de log
accesslog = "-"
errorlog = "-"

# Niveau de log
loglevel = "info"

# Activer le reloading en développement (désactivé en production)
# reload = True

# Fichier WSGI
wsgi_app = "wsgi:app"
