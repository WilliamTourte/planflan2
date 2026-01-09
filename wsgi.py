"""Fichier WSGI pour l'application PlanFlan.

Ce fichier est utilisé par les serveurs WSGI comme Gunicorn ou uWSGI pour lancer l'application Flask.
"""

from app import create_app

# Créer l'application Flask avec la configuration par défaut
app = create_app()

if __name__ == "__main__":
    # Ce bloc est utile pour tester le fichier wsgi.py directement
    # Exemple : python wsgi.py
    app.run(host="0.0.0.0", port=5000)
