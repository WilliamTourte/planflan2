from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from app.models import  TypeEtab, Etablissement, Flan, db
# Configuration minimale de Flask et SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/planflan_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


def inserer_jeu_de_donnees():
    with app.app_context():  # Crée un contexte d'application
        # Effacer les données existantes (optionnel)
        db.session.query(Flan).delete()
        db.session.query(Etablissement).delete()
        db.session.commit()

        # Ajouter les établissements
        etablissements = [
            Etablissement(
                id_etab=1,
                type_etab=TypeEtab.BOULANGERIE,
                nom="Boulangerie Martin",
                adresse="12 rue de Paris",
                code_postal="75001",
                ville="Paris",
                latitude=48.8606,
                longitude=2.3376,
                telephone="0123456789",
                site_web="www.martin.fr",
                description="Meilleure boulangerie du quartier.",
                label=True,
                visite=True
            ),
            Etablissement(
                id_etab=2,
                type_etab=TypeEtab.CAFE,
                nom="Café des Flans",
                adresse="45 avenue de Lyon",
                code_postal="69002",
                ville="Lyon",
                latitude=45.7640,
                longitude=4.8357,
                telephone="0478901234",
                site_web="www.cafedesflans.fr",
                description="Café spécialisé en flans maison.",
                label=False,
                visite=True
            ),
            Etablissement(
                id_etab=3,
                type_etab=TypeEtab.RESTAURANT,
                nom="Le Flan Gourmand",
                adresse="78 boulevard de Bordeaux",
                code_postal="33000",
                ville="Bordeaux",
                latitude=44.8378,
                longitude=-0.5792,
                telephone="0556789012",
                site_web="www.leflangourmand.fr",
                description="Restaurant avec une carte de flans.",
                label=True,
                visite=False
            )
        ]
        db.session.add_all(etablissements)
        db.session.commit()

        # Ajouter les flans
        flans = [
            Flan(id_flan=1, id_etab=1, nom="Flan nature", description="Classique, vanille."),
            Flan(id_flan=2, id_etab=1, nom="Flan chocolat", description="Ganache chocolat noir."),
            Flan(id_flan=3, id_etab=2, nom="Flan coco", description="Noix de coco râpée."),
            Flan(id_flan=4, id_etab=3, nom="Flan caramel", description="Caramel maison et sel de Guérande.")
        ]
        db.session.add_all(flans)
        db.session.commit()
        print("Jeu de données inséré avec succès !")

if __name__ == '__main__':
    inserer_jeu_de_donnees()
inserer_jeu_de_donnees()