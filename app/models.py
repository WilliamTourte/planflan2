from enum import Enum

from app import login_manager, db, bcrypt # importe la base de données
from flask_login import UserMixin


class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    email = db.Column('email', db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    is_ambad = db.Column(db.Boolean, nullable=True, default=False)
    is_ambadx = db.Column(db.Boolean, nullable=True, default=False)
    # Relation avec les évaluations
    evaluations = db.relationship('Evaluation', back_populates='user')


    def get_id(self):
        return str(self.id_user)

    def set_password(self, password, bcrypt):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def email(self):
        return self.email
    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("L'adresse email doit contenir un @.")
        self._email = value # Stocke dans un attribut privé




class TypeEtab(Enum):
    BOULANGERIE = 'Boulangerie'
    PATISSERIE = "Pâtisserie"
    RESTAURANT = 'Restaurant'
    CAFE = "Coffee Shop"

from app import db
from enum import Enum
import re

class TypeEtab(Enum):
    BOULANGERIE = "Boulangerie"
    RESTAURANT = "Restaurant"
    CAFE = "Café"

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
    telephone = db.Column('telephone', db.String(20), nullable=True)
    site_web = db.Column('site_web', db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    label = db.Column(db.Boolean, nullable=True, default=False)
    visite = db.Column(db.Boolean, nullable=True, default=False)
    flans = db.relationship('Flan', back_populates='etablissement', lazy=True)
    photos = db.relationship('Photo', backref='etablissement_photo', lazy=True, foreign_keys='Photo.id_etab')

    @property
    def telephone(self):
        return self._telephone

    @telephone.setter
    def telephone(self, value):
        if value is not None and not re.match(r'^\+?[0-9\s\-\(\)]{10,}$', value):
            raise ValueError("Numéro de téléphone invalide")
        self._telephone = value # Stocke dans un attribut privé

    @property
    def site_web(self):
        return self._site_web

    @site_web.setter
    def site_web(self, value):
        if value is not None and not re.match(r'^https?://.+', value):
            raise ValueError("L'URL du site web doit commencer par http:// ou https://")
        self._site_web = value # Stocke dans un attribut privé

    @property
    def code_postal(self):
        return self._code_postal

    @code_postal.setter
    def code_postal(self, value):
        if not re.match(r'^\d{5}$', value):
            raise ValueError("Le code postal doit être composé de 5 chiffres")
        self._code_postal = value # Stocke dans un attribut privé

    _code_postal = db.Column('code_postal', db.String(5), nullable=False)


class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    # Relation avec les évaluations
    evaluations = db.relationship('Evaluation', back_populates='flan', lazy=True)
    # Relation avec les photos
    photos = db.relationship('Photo', backref='flan_photo', lazy=True, foreign_keys='Photo.id_flan')
    # Relation avec Etablissement
    etablissement = db.relationship('Etablissement', back_populates='flans')

    @property
    def prix(self):
        return self._prix

    @prix.setter
    def prix(self, value):
        if value is not None and value < 0:
            raise ValueError("Le prix ne peut pas être négatif")
        self._prix = value


class StatutEval(Enum): # Avantage de Enum : vérification des valeurs
    EN_ATTENTE = 'EN_ATTENTE'
    VALIDE = 'VALIDE'
    SUPPRIME = 'SUPPRIME'

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id_eval = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=False)
    id_flan = db.Column(db.Integer, db.ForeignKey('flans.id_flan'), nullable=False)
    visuel = db.Column(db.Numeric(2, 1), nullable=False)
    texture = db.Column(db.Numeric(2, 1), nullable=False)
    pate = db.Column(db.Numeric(2, 1), nullable=False)
    gout = db.Column(db.Numeric(2, 1), nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    statut = db.Column(db.Enum(StatutEval), nullable=False, server_default='EN_ATTENTE')
    date_creation = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    moyenne = db.Column(db.Numeric(2, 1), nullable=True)

    # Relation avec Utilisateur
    user = db.relationship('Utilisateur', back_populates='evaluations')
    # Relation avec Flan
    flan = db.relationship('Flan', back_populates='evaluations')


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


