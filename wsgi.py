# Fichier WSGI pour l'application Flask

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
