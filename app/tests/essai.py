from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

# Configuration minimale de Flask et SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/planflan_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# Définition des modèles (à copier depuis ton projet)
class TypeEtab(Enum):
    BOULANGERIE = 'Boulangerie'
    RESTAURANT = 'Restaurant'
    CAFE = 'Café'

class Etablissement(db.Model):
    __tablename__ = 'etablissements'
    id_etab = db.Column(db.Integer, primary_key=True)
    type_etab = db.Column(db.Enum(TypeEtab), nullable=False, default=TypeEtab.BOULANGERIE)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    code_postal = db.Column(db.String(5), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    site_web = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    label = db.Column(db.Boolean, nullable=True, default=False)
    visite = db.Column(db.Boolean, nullable=True, default=False)
    flans = db.relationship('Flan', backref='etablissement', lazy=True)

class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

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