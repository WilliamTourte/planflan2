from sqlalchemy import create_engine, MetaData, Table, select, insert, delete
from sqlalchemy.orm import sessionmaker
import random
from enum import Enum


# Définition des énumérations
class TypePate(Enum):
    FEUILLETEE = "Feuilletée"
    BRISEE = "Brisée"
    SUCREE = "Sucrée"
    SABLEE = "Sablée"
    MIXTE = "Mixte"


class TypeSaveur(Enum):
    VANILLE = "Vanille"
    NOIX = "Noix"
    FRUITS = "Fruits"
    INSOLITE = "Insolite"
    NATURE = "Nature"


class TypeTexture(Enum):
    GELATINEUSE = "Gélatineuse"
    CREMEUSE = "Crémeuse"
    COSTAUD = "Costaud"
    OEUF = "Oeuf"
    MIX_PARFAIT = "Mix parfait"


# Configuration de la connexion à la base de données
DATABASE_URI = "mysql+pymysql://flask_user:flanflask@localhost/planflan_db"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Récupérer les tables
metadata = MetaData()
etablissements = Table("etablissements", metadata, autoload_with=engine)
flans = Table("flans", metadata, autoload_with=engine)

# 1. Supprimer tous les flans existants
session.execute(delete(flans))
session.commit()
print("✅ Tous les flans existants ont été supprimés.")

# Récupérer tous les établissements
query = select(etablissements)
result = session.execute(query)
etablissement_records = result.fetchall()

# Liste de noms de flans
noms_flans = [
    "Flan Vanille",
    "Flan Chocolat",
    "Flan Caramel",
    "Flan Café",
    "Flan Noisette",
    "Flan Citron",
]

# Liste de descriptions
descriptions = [
    "Un délicieux flan à la vanille.",
    "Un flan au chocolat riche et crémeux.",
    "Un flan au caramel avec une touche de sel.",
    "Un flan au café pour les amateurs de café.",
    "Un flan à la noisette avec une texture onctueuse.",
    "Un flan au citron rafraîchissant.",
]

# 2. Créer des flans aléatoires pour chaque établissement
for etablissement in etablissement_records:
    # Générer un nombre aléatoire de flans (entre 1 et 3)
    num_flans = random.randint(1, 3)
    for _ in range(num_flans):
        # Générer des données aléatoires
        nom = random.choice(noms_flans)
        description = random.choice(descriptions)
        prix = round(random.uniform(2.0, 5.0), 2)
        type_pate = random.choice(list(TypePate)).name
        type_saveur = random.choice(list(TypeSaveur)).name
        type_texture = random.choice(list(TypeTexture)).name

        # Insérer le flan
        stmt = insert(flans).values(
            id_etab=etablissement.id_etab,
            nom=nom,
            description=description,
            prix=prix,
            type_pate=type_pate,
            type_saveur=type_saveur,
            type_texture=type_texture,
            id_user=1,
        )
        session.execute(stmt)

# Valider les modifications
session.commit()
print(
    f"✅ {len(etablissement_records)} établissements mis à jour avec des flans aléatoires."
)
session.close()
