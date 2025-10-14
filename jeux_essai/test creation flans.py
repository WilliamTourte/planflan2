from sqlalchemy import create_engine, MetaData, Table, select, insert
from sqlalchemy.orm import sessionmaker
import random

# Configuration de la connexion à la base de données
DATABASE_URI = 'mysql://root:@localhost/planflan_db'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Récupérer la table Etablissement
metadata = MetaData()
etablissements = Table('etablissements', metadata, autoload_with=engine)
flans = Table('flans', metadata, autoload_with=engine)

# Récupérer tous les établissements
query = select(etablissements)
result = session.execute(query)
etablissement_records = result.fetchall()

# Liste de noms de flans pour générer des noms aléatoires
noms_flans = ["Flan Vanille", "Flan Chocolat", "Flan Caramel", "Flan Café", "Flan Noisette", "Flan Citron"]

# Liste de descriptions pour générer des descriptions aléatoires
descriptions = [
    "Un délicieux flan à la vanille.",
    "Un flan au chocolat riche et crémeux.",
    "Un flan au caramel avec une touche de sel.",
    "Un flan au café pour les amateurs de café.",
    "Un flan à la noisette avec une texture onctueuse.",
    "Un flan au citron rafraîchissant."
]

# Mettre à jour chaque établissement avec des flans aléatoires
for etablissement in etablissement_records:
    # Générer un nombre aléatoire de flans (entre 0 et 3)
    num_flans = random.randint(0, 3)
    for _ in range(num_flans):
        # Générer des données aléatoires pour chaque flan
        nom = random.choice(noms_flans)
        description = random.choice(descriptions)
        prix = round(random.uniform(2.0, 5.0), 2)  # Prix entre 2.0 et 5.0 euros

        # Insérer le flan dans la base de données
        stmt = insert(flans).values(
            id_etab=etablissement.id_etab,
            nom=nom,
            description=description,
            prix=prix
        )
        session.execute(stmt)

# Valider les modifications
session.commit()
session.close()
