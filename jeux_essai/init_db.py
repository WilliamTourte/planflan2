from app import create_app, db

app = create_app() # Crée l'application Flask et l'instancie
with app.app_context():
    db.create_all() # Crée les tables nécessaires si elles n'existent pas déjà