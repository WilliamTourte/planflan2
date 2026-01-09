import logging
from app import create_app, db

# Configuration du logging
logging.basicConfig(
    filename="database.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = create_app()  # Crée l'application Flask et l'instancie
with app.app_context():
    logger.info("Création des tables de la base de données")
    db.create_all()  # Crée les tables nécessaires si elles n'existent pas déjà
    logger.info("Tables créées avec succès")
