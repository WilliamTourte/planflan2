from enum import Enum
from app import db
from flask_login import UserMixin

class TypeEtab(Enum):
    BOULANGERIE = 'Boulangerie'
    PATISSERIE = "Pâtisserie"
    RESTAURANT = 'Restaurant'
    CAFE = "Coffee Shop"

class StatutModeration(Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    VALIDE = 'VALIDE'
    SUPPRIME = 'SUPPRIME'

class TypeCible(Enum):
    FLAN = 'Flan'
    ETABLISSEMENT = 'Etablissement'

class TypePate(Enum):
    FEUILLETEE = 'Feuilletée'
    BRISEE = 'Brisée'
    SUCREE = 'Sucrée'
    SABLEE = 'Sablée'
    SABLEE_DIAMANT = 'Sablée Diamant'

class Utilisateur(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)

    # Relations
    etablissements = db.relationship('Etablissement', back_populates='utilisateur')
    flans = db.relationship('Flan', back_populates='utilisateur')
    evaluations = db.relationship('Evaluation', back_populates='utilisateur')

    def get_id(self):
        return str(self.id_user)

    def set_password(self, password, bcrypt):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password, password)

class Etablissement(db.Model):
    __tablename__ = 'etablissements'
    id_etab = db.Column(db.Integer, primary_key=True)
    type_etab = db.Column(db.Enum(TypeEtab), nullable=False, default=TypeEtab.BOULANGERIE)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    code_postal = db.Column(db.String(5), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(10, 8), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    site_web = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    label = db.Column(db.Boolean, nullable=True, default=False)
    visite = db.Column(db.Boolean, nullable=True, default=False)
    statut = db.Column(db.Enum(StatutModeration), nullable=False, server_default='EN_ATTENTE')

    # Clé étrangère pour l'utilisateur
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=True, index=True)  # /!\ Null temporaire !! DEBUG

    # Relations
    flans = db.relationship('Flan', back_populates='etablissement', lazy=True)
    photos = db.relationship('Photo', back_populates='etablissement', foreign_keys='Photo.id_etab')
    utilisateur = db.relationship('Utilisateur', back_populates='etablissements')

class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    type_pate = db.Column(db.Enum(TypePate), nullable=True)
    statut = db.Column(db.Enum(StatutModeration), nullable=False, server_default='EN_ATTENTE')

    # Clé étrangère pour l'utilisateur
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=True, index=True) # /!\ Null temporaire !! DEBUG

    # Relations
    evaluations = db.relationship('Evaluation', back_populates='flan', lazy=True)
    photos = db.relationship('Photo', back_populates='flan', foreign_keys='Photo.id_flan')
    etablissement = db.relationship('Etablissement', back_populates='flans')
    utilisateur = db.relationship('Utilisateur', back_populates='flans')

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
    statut = db.Column(db.Enum(StatutModeration), nullable=False, server_default='EN_ATTENTE')
    date_creation = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    moyenne = db.Column(db.Numeric(2, 1), nullable=True)

    # Relations
    utilisateur = db.relationship('Utilisateur', back_populates='evaluations')
    flan = db.relationship('Flan', back_populates='evaluations')

class Photo(db.Model):
    __tablename__ = 'photos'
    id_photo = db.Column(db.Integer, primary_key=True)
    id_flan = db.Column(db.Integer, db.ForeignKey('flans.id_flan'), nullable=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=True)
    type_cible = db.Column(db.Enum(TypeCible), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    largeur = db.Column(db.Integer, nullable=False)
    hauteur = db.Column(db.Integer, nullable=False)

    # Relations
    etablissement = db.relationship('Etablissement', back_populates='photos')
    flan = db.relationship('Flan', back_populates='photos')

