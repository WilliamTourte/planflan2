from enum import Enum

from app import login_manager, bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False) # par défaut un utilisateur n'est pas administrateur'

    # Relation avec les évaluations
    evaluations = db.relationship('Evaluation', backref='utilisateur', lazy=True)

    def get_id(self): # Pour que get_id de Flask Login utilise l'id_user' plutôt que 'id' par défaut
        return str(self.id_user)

    def set_password(self, password): # Hache le mot de passe
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password): # Vérifie que le mot de passe est correct
        return bcrypt.check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id): # Prend un user_id pour charger un utilisateur
    return Utilisateur.query.get(int(user_id))

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

    # Relation avec les flans
    flans = db.relationship('Flan', backref='etablissement', lazy=True)
    # Relation avec les photos
    photos = db.relationship('Photo', backref='etablissement_photo', lazy=True, foreign_keys='Photo.id_etab')

class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relation avec les évaluations
    evaluations = db.relationship('Evaluation', backref='flan', lazy=True)
    # Relation avec les photos
    photos = db.relationship('Photo', backref='flan_photo', lazy=True, foreign_keys='Photo.id_flan')

class StatutEval(Enum):
    EN_ATTENTE = 'En attente'
    VALIDE = 'Validé'
    SUPPRIME = 'Supprimé'

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id_eval = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=False)
    id_flan = db.Column(db.Integer, db.ForeignKey('flans.id_flan'), nullable=False)
    visuel = db.Column(db.Numeric(2, 1), nullable=False)
    texture = db.Column(db.Numeric(2, 1), nullable=False)
    pate = db.Column(db.Numeric(2, 1), nullable=False)
    gout = db.Column(db.Numeric(2, 1), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    statut = db.Column(db.Enum(StatutEval), nullable=False, default=StatutEval.EN_ATTENTE)
    date_creation = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    moyenne = db.Column(db.Numeric(2, 1), nullable=True)

class TypeCible(Enum):
    FLAN = 'Flan'
    ETABLISSEMENT = 'Etablissement'

class Photo(db.Model):
    __tablename__ = 'photos'
    id_photo = db.Column(db.Integer, primary_key=True)
    id_flan = db.Column(db.Integer, db.ForeignKey('flans.id_flan'), nullable=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=True)
    type_cible = db.Column(db.Enum(TypeCible), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    largeur = db.Column(db.Integer, nullable=False)
    hauteur = db.Column(db.Integer, nullable=False)


