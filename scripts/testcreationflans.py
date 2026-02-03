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
evaluations = Table("evaluations", metadata, autoload_with=engine)

# 1. Supprimer tous les flans existants
session.execute(delete(flans))
session.commit()
print("✅ Tous les flans existants ont été supprimés.")

# 2. Supprimer toutes les évaluations existantes
session.execute(delete(evaluations))
session.commit()
print("✅ Toutes les évaluations existantes ont été supprimées.")

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

# 3. Créer des flans aléatoires pour chaque établissement
flans_crees = []
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
            statut="VALIDE",
        )
        result = session.execute(stmt)
        flans_crees.append(
            {"id_flan": result.lastrowid, "id_etab": etablissement.id_etab, "nom": nom}
        )

# Valider les modifications
session.commit()
print(f"✅ {len(etablissement_records)} établissements mis à jour avec des flans aléatoires.")

# 4. Créer des évaluations aléatoires pour les flans des établissements visités
# Récupérer les établissements avec visite = True
query_visites = select(etablissements).where(etablissements.c.visite == True)
result_visites = session.execute(query_visites)
etablissements_visites = result_visites.fetchall()

evaluations_crees = 0
for etablissement in etablissements_visites:
    # Trouver les flans de cet établissement
    flans_etab = [f for f in flans_crees if f["id_etab"] == etablissement.id_etab]

    if flans_etab:
        # Créer des évaluations pour certains flans (entre 1 et le nombre total de flans)
        num_evaluations = random.randint(1, len(flans_etab))
        flans_a_evaluer = random.sample(flans_etab, num_evaluations)

        for flan in flans_a_evaluer:
            # Générer des notes aléatoires (entre 1 et 5 avec 1 décimale)
            visuel = round(random.uniform(1.0, 5.0), 1)
            texture = round(random.uniform(1.0, 5.0), 1)
            pate = round(random.uniform(1.0, 5.0), 1)
            gout = round(random.uniform(1.0, 5.0), 1)

            # Insérer l'évaluation
            stmt_eval = insert(evaluations).values(
                visuel=visuel,
                texture=texture,
                pate=pate,
                gout=gout,
                id_flan=flan["id_flan"],
                id_user=1,  # admin_flan
                statut="TypVALIDE",
            )
            session.execute(stmt_eval)
            evaluations_crees += 1
            print(f"✅ Évaluation créée pour {flan['nom']} (ID: {flan['id_flan']})")

# Valider les modifications des évaluations
session.commit()
print(f"✅ {evaluations_crees} évaluations aléatoires créées pour les établissements visités.")

session.close()
