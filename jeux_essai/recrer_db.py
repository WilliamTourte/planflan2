import re
import json
import os
import sys
import random
import logging
from enum import Enum
from sqlalchemy import create_engine, MetaData, Table, select, insert, delete, update
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    filename='database.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement en premier
load_dotenv()

# Ajouter le chemin du projet pour importer le module app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Définition des énumérations pour les flans
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

# Configuration pour SQLAlchemy direct (pour les fonctions d'import)
DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://flask_user:flanflask@localhost/planflan_db")

# Import de l'application Flask après avoir configuré le chemin
try:
    from app import create_app, db, bcrypt
    print("Import de l'application Flask reussi")
except ImportError as e:
    print(f"Erreur d'import de l'application Flask : {e}")
    print(f"Chemin du projet ajoute : {project_root}")
    print(f"Contenu du dossier : {os.listdir(project_root)}")
    sys.exit(1)

# Créer l'instance de l'application
app = create_app()

def extraire_code_postal(adresse):
    match = re.search(r"(\d{5})", adresse)
    return match.group(1) if match else None

def extraire_ville(adresse):
    match = re.search(r"\d{5}\s+([^,]+)", adresse)
    return match.group(1).strip() if match else None

def nettoyer_adresse(adresse):
    return adresse.split(",")[0].strip()

def importer_lieux(fichier_json):
    print("Debut de l'import...")
    if not os.path.exists(fichier_json):
        print(f"Fichier introuvable : {fichier_json}")
        return
    
    try:
        with open(fichier_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Nombre de lieux : {len(data.get('features', []))}")
            
            with app.app_context():
                from app.models import Etablissement
                
                for feature in data["features"]:
                    try:
                        nom = feature["properties"]["location"]["name"]
                        adresse_complete = feature["properties"]["location"]["address"]
                        longitude = feature["geometry"]["coordinates"][0]
                        latitude = feature["geometry"]["coordinates"][1]
                        adresse = nettoyer_adresse(adresse_complete)
                        code_postal = extraire_code_postal(adresse_complete)
                        ville = extraire_ville(adresse_complete)
                        
                        if not Etablissement.query.filter_by(
                            nom=nom, adresse=adresse
                        ).first():
                            lieu = Etablissement(
                                nom=nom,
                                adresse=adresse,
                                code_postal=code_postal,
                                ville=ville,
                                latitude=latitude,
                                longitude=longitude,
                                type_etab="BOULANGERIE",
                                id_user=1,
                            )
                            db.session.add(lieu)
                            print(f"✅ Ajout : {nom}")
                        else:
                            print(f"Deja present : {nom}")
                    except Exception as e:
                        print(
                            f"Erreur sur {feature.get('properties', {}).get('location', {}).get('name', 'inconnu')}: {e}"
                        )
                db.session.commit()
                print("Import termine !")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur globale : {e}")

def creer_flans_et_evaluations():
    """Fonction pour créer des flans et des évaluations aléatoires"""
    print("🍮 Création des flans et évaluations...")
    logger.info("Début de la création des flans et évaluations")
    
    # Créer un engine SQLAlchemy pour les opérations directes
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Récupérer les tables
    metadata = MetaData()
    etablissements = Table("etablissements", metadata, autoload_with=engine)
    flans = Table("flans", metadata, autoload_with=engine)
    evaluations = Table("evaluations", metadata, autoload_with=engine)
    
    # 1. Supprimer tous les flans existants
    logger.info("Suppression de tous les flans existants")
    session.execute(delete(flans))
    session.commit()
    print("Tous les flans existants ont ete supprimes.")
    logger.info("Tous les flans existants ont été supprimés")
    
    # 2. Supprimer toutes les évaluations existantes
    logger.info("Suppression de toutes les évaluations existantes")
    session.execute(delete(evaluations))
    session.commit()
    print("Toutes les evaluations existantes ont ete supprimees.")
    logger.info("Toutes les évaluations existantes ont été supprimées")
    
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
            )
            result = session.execute(stmt)
            flans_crees.append({
                'id_flan': result.lastrowid,
                'id_etab': etablissement.id_etab,
                'nom': nom
            })
    
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
        flans_etab = [f for f in flans_crees if f['id_etab'] == etablissement.id_etab]
        
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
                    id_flan=flan['id_flan'],
                    id_user=1,  # admin_flan
                )
                session.execute(stmt_eval)
                evaluations_crees += 1
                print(f"✅ Évaluation créée pour {flan['nom']} (ID: {flan['id_flan']})")
    
    # Valider les modifications des évaluations
    session.commit()
    print(f"✅ {evaluations_crees} évaluations aléatoires créées pour les établissements visités.")
    
    session.close()

def mettre_a_jour_visite_label():
    """Fonction pour mettre à jour les champs visite et label des établissements"""
    print("Mise a jour des champs visite et label...")
    logger.info("Début de la mise à jour des champs visite et label")
    
    # Créer un engine SQLAlchemy
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Récupérer la table Etablissement
    metadata = MetaData()
    etablissements = Table("etablissements", metadata, autoload_with=engine)
    
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
        stmt = (
            update(etablissements)
            .where(etablissements.c.id_etab == etablissement.id_etab)
            .values(visite=visite, label=label)
        )
        session.execute(stmt)
    
    # Valider les modifications
    session.commit()
    print(f"{len(etablissement_records)} etablissements mis a jour avec visite/label aleatoires.")
    logger.info(f"{len(etablissement_records)} établissements mis à jour avec visite/label aléatoires")
    session.close()

# Fonction principale
if __name__ == "__main__":
    print("Debut de la recreation de la base de donnees...")
    logger.info("Début de la recréation de la base de données")
    
# Crée le contexte d'application
with app.app_context():

    # Crée toutes les tables
    logger.info("Création de toutes les tables")
    db.create_all()

    # Importe les modèles après la création de l'app
    from app.models import (
        Utilisateur,
        StatutModeration
    )

    # Exemple : Création d'un utilisateur admin (uniquement s'il n'existe pas)
    try:
        admin = Utilisateur.query.filter_by(pseudo="flan_admin").first()
        if not admin:
            print("👤 Création de l'utilisateur flan_admin...")
            logger.info("Création de l'utilisateur flan_admin")
            admin = Utilisateur(pseudo="flan_admin", email="admin@example.com", is_admin=True)
            admin.set_password("flan_password", bcrypt)
            db.session.add(admin)
        else:
            print("Utilisateur flan_admin existe deja, pas de recreation")
            logger.info("Utilisateur flan_admin existe déjà, pas de recréation")
    except Exception as e:
        print(f"Erreur lors de la verification/creation de l'utilisateur : {e}")
        logger.error(f"Erreur lors de la vérification/création de l'utilisateur : {e}")
        db.session.rollback()



    # Valide les changements
    db.session.commit()

    print("Tables recreees avec succes !")
    logger.info("Tables recréées avec succès")
    print("Tables disponibles :")
    for table_name in db.metadata.tables.keys():
        print(f"  - {table_name}")
    
    # Import des lieux - chercher d'abord dans le dossier jeux_essai
    dossier_jeux_essai = os.path.dirname(os.path.abspath(__file__))
    chemin_lieux_json = os.path.join(dossier_jeux_essai, "lieux_test.json")
    
    if os.path.exists(chemin_lieux_json):
        print(f"Fichier lieux_test.json trouve dans jeux_essai : {chemin_lieux_json}")
        logger.info(f"Fichier lieux_test.json trouvé dans jeux_essai : {chemin_lieux_json}")
        importer_lieux(chemin_lieux_json)
    else:
        print("Aucun fichier lieux_test.json trouve dans jeux_essai")
        logger.info("Aucun fichier lieux_test.json trouvé dans jeux_essai")
        if len(sys.argv) > 1:
            fichier_json = sys.argv[1]
            if os.path.exists(fichier_json):
                importer_lieux(fichier_json)
            else:
                print(f"Fichier specifie introuvable : {fichier_json}")
                logger.error(f"Fichier spécifié introuvable : {fichier_json}")
        else:
            print("Pour importer des lieux, utilisez : python recrer_db.py chemin/vers/fichier.json")
            logger.info("Pour importer des lieux, utilisez : python recrer_db.py chemin/vers/fichier.json")
    
    # Mise à jour des champs visite et label
    mettre_a_jour_visite_label()
    
    # Création des flans et évaluations
    creer_flans_et_evaluations()
    
    print("🎉 Recréation de la base de données terminée avec succès !")
    logger.info("Recréation de la base de données terminée avec succès")
