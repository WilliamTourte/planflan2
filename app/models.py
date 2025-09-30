from enum import Enum
from app import login_manager, db, bcrypt
from flask_login import UserMixin
import re

# --- Enums ---
class TypeEtab(Enum):
    BOULANGERIE = "Boulangerie"
    PATISSERIE = "Pâtisserie"
    RESTAURANT = "Restaurant"
    CAFE = "Coffee Shop"

class StatutEval(Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    VALIDE = 'VALIDE'
    SUPPRIME = 'SUPPRIME'

class TypeCible(Enum):
    FLAN = 'Flan'
    ETABLISSEMENT = 'Etablissement'

# --- Modèles ---
class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)
    is_ambad = db.Column(db.Boolean, nullable=True, default=False)
    is_ambadx = db.Column(db.Boolean, nullable=True, default=False)
    evaluations = db.relationship('Evaluation', back_populates='user')

    def get_id(self):
        return str(self.id_user)

    def set_password(self, password, bcrypt):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def email(self):
        return self.__dict__.get('email')

    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("L'adresse email doit contenir un @.")
        self.__dict__['email'] = value

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
    flans = db.relationship('Flan', back_populates='etablissement', lazy=True)
    photos = db.relationship('Photo', backref='etablissement_photo', lazy=True, foreign_keys='Photo.id_etab')

    @property
    def telephone(self):
        return self.__dict__.get('telephone')

    @telephone.setter
    def telephone(self, value):
        if value is not None and not re.match(r'^\+?[0-9\s\-\(\)]{10,}$', value):
            raise ValueError("Numéro de téléphone invalide")
        self.__dict__['telephone'] = value

    @property
    def site_web(self):
        return self.__dict__.get('site_web')

    @site_web.setter
    def site_web(self, value):
        if value is not None and not re.match(r'^https?://.+', value):
            raise ValueError("L'URL du site web doit commencer par http:// ou https://")
        self.__dict__['site_web'] = value

    @property
    def code_postal(self):
        return self.__dict__.get('code_postal')

    @code_postal.setter
    def code_postal(self, value):
        if not re.match(r'^\d{5}$', value):
            raise ValueError("Le code postal doit être composé de 5 chiffres")
        self.__dict__['code_postal'] = value

class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    evaluations = db.relationship('Evaluation', back_populates='flan', lazy=True)
    photos = db.relationship('Photo', backref='flan_photo', lazy=True, foreign_keys='Photo.id_flan')
    etablissement = db.relationship('Etablissement', back_populates='flans')

    @property
    def prix(self):
        return self.__dict__.get('prix')

    @prix.setter
    def prix(self, value):
        if value is not None and value < 0:
            raise ValueError("Le prix ne peut pas être négatif")
        self.__dict__['prix'] = value

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
    user = db.relationship('Utilisateur', back_populates='evaluations')
    flan = db.relationship('Flan', back_populates='evaluations')

    @property
    def visuel(self):
        return self.__dict__.get('visuel')

    @visuel.setter
    def visuel(self, value):
        if not 0 <= value <= 5:
            raise ValueError("La note doit être entre 0 et 5")
        self.__dict__['visuel'] = value

    @property
    def texture(self):
        return self.__dict__.get('texture')

    @texture.setter
    def texture(self, value):
        if not 0 <= value <= 5:
            raise ValueError("La note doit être entre 0 et 5")
        self.__dict__['texture'] = value

    @property
    def pate(self):
        return self.__dict__.get('pate')

    @pate.setter
    def pate(self, value):
        if not 0 <= value <= 5:
            raise ValueError("La note doit être entre 0 et 5")
        self.__dict__['pate'] = value

    @property
    def gout(self):
        return self.__dict__.get('gout')

    @gout.setter
    def gout(self, value):
        if not 0 <= value <= 5:
            raise ValueError("La note doit être entre 0 et 5")
        self.__dict__['gout'] = value

class Photo(db.Model):
    __tablename__ = 'photos'
    id_photo = db.Column(db.Integer, primary_key=True)
    id_flan = db.Column(db.Integer, db.ForeignKey('flans.id_flan'), nullable=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=True)
    type_cible = db.Column(db.Enum(TypeCible), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    largeur = db.Column(db.Integer, nullable=False)
    hauteur = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))
