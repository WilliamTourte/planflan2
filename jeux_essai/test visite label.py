from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.orm import sessionmaker
import random

# Configuration de la connexion à la base de données
# Remplacez par vos informations de connexion
DATABASE_URI = 'mysql://root:@localhost/planflan_db'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Récupérer la table Etablissement
metadata = MetaData()
etablissements = Table('etablissements', metadata, autoload_with=engine)

# Récupérer tous les établissements
query = select(etablissements)
result = session.execute(query)
etablissement_records = result.fetchall()

# Mettre à jour chaque établissement avec des valeurs aléatoires
for etablissement in etablissement_records:
    visite = random.choice([0, 1])
    label = 0
    if visite == 1:
        label = random.choice([0, 1])
    # Mettre à jour l'enregistrement
    stmt = update(etablissements).where(etablissements.c.id_etab == etablissement.id_etab).values(visite=visite, label=label)
    session.execute(stmt)

# Valider les modifications
session.commit()
session.close()
