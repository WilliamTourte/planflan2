from enum import Enum
from flask_login import UserMixin
from flask import url_for
from app import db


# Enumérations
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
    MIXTE = 'Mixte'

class TypeSaveur(Enum):
    VANILLE = "Vanille"
    CHOCOLAT = "Chocolat"
    NOIX = "Noix"
    FRUITS = "Fruits"
    INSOLITE = 'Insolite'
    NATURE = 'Nature'

class TypeTexture(Enum):
    GELATINEUSE = 'Gélatineuse'
    CREMEUSE = 'Crémeuse'
    FONDANTE = 'Fondante'
    COSTAUD = 'Costaud'
    OEUF = 'Oeuf'
    MIX_PARFAIT = 'Mix parfait'

# Classes base de données avec SQLAlchemy
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

    def to_dict(self):
        return {
            'id_user': self.id_user,
            'pseudo': self.pseudo,
            'email': self.email,
            'is_admin': self.is_admin,
            # Ne sérialise pas les relations pour éviter les boucles
            # (utilise des endpoints dédiés si besoin)
        }

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
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=False, index=True, server_default='1')

    # Relations
    flans = db.relationship('Flan', back_populates='etablissement', lazy=True,cascade="all, delete-orphan")
    photos = db.relationship('Photo', back_populates='etablissement', foreign_keys='Photo.id_etab')
    utilisateur = db.relationship('Utilisateur', back_populates='etablissements')

    def to_dict(self, include_flans=True, include_photos=False):
        data = {
            'id_etab': self.id_etab,
            'type_etab': self.type_etab.value if self.type_etab else None,
            'nom': self.nom,
            'adresse': self.adresse,
            'code_postal': self.code_postal,
            'ville': self.ville,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'telephone': self.telephone,
            'site_web': self.site_web,
            'description': self.description,
            'label': self.label,
            'visite': self.visite,
            'statut': self.statut.value if self.statut else None,
            'id_user': self.id_user,
            'url': url_for('main.afficher_etablissement_unique', id_etab=self.id_etab),
        }

        if include_flans:
            data['flans'] = [flan.to_dict(include_etablissement=False) for flan in self.flans]

        if include_photos:
            data['photos'] = [photo.to_dict() for photo in self.photos]

        
        return data

class Flan(db.Model):
    __tablename__ = 'flans'
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(db.Integer, db.ForeignKey('etablissements.id_etab'), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    type_saveur = db.Column(db.Enum(TypeSaveur), nullable=True)
    type_pate = db.Column(db.Enum(TypePate), nullable=True)
    type_texture = db.Column(db.Enum(TypeTexture), nullable=True)
    statut = db.Column(db.Enum(StatutModeration), nullable=False, server_default='EN_ATTENTE')

    # Clé étrangère pour l'utilisateur
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=False, index=True, default="1")

    # Relations
    evaluations = db.relationship('Evaluation', back_populates='flan', lazy=True, cascade="all, delete-orphan")
    photos = db.relationship('Photo', back_populates='flan', foreign_keys='Photo.id_flan')
    etablissement = db.relationship('Etablissement', back_populates='flans')
    utilisateur = db.relationship('Utilisateur', back_populates='flans')

    def get_moyenne_evaluations(self):
        """Calcule la moyenne des évaluations pour ce flan.
        
        Returns:
            float: La moyenne des moyennes des évaluations, ou None si pas d'évaluations.
        """
        if not self.evaluations:
            return None
        
        # Filtrer les évaluations valides avec une moyenne
        evaluations_valides = [eval for eval in self.evaluations 
                              if eval.moyenne is not None]
        
        if not evaluations_valides:
            return None
            
        # Calculer la moyenne des moyennes
        somme = sum(float(eval.moyenne) for eval in evaluations_valides)
        return round(somme / len(evaluations_valides), 1)

    def to_dict(self, include_etablissement=True, include_evaluations=True, include_photos=False):
        data = {
            'id_flan': self.id_flan,
            'id_etab': self.id_etab,
            'nom': self.nom,
            'description': self.description,
            'prix': float(self.prix) if self.prix else None,
            'type_saveur': self.type_saveur.value if self.type_saveur else None,
            'type_pate': self.type_pate.value if self.type_pate else None,
            'type_texture': self.type_texture.value if self.type_texture else None,
            'statut': self.statut.value if self.statut else None,
            'id_user': self.id_user,
        }

        if include_etablissement:
            data['etablissement'] = self.etablissement.to_dict(include_flans=False)

        if include_evaluations:
            data['evaluations'] = [eval.to_dict(include_flan=False) for eval in self.evaluations]

        if include_photos:
            data['photos'] = [photo.to_dict() for photo in self.photos]

        return data

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

    def to_dict(self, include_flan=False, include_utilisateur=False):
        data = {
            'id_eval': self.id_eval,
            'id_user': self.id_user,
            'id_flan': self.id_flan,
            'visuel': float(self.visuel) if self.visuel else None,
            'texture': float(self.texture) if self.texture else None,
            'pate': float(self.pate) if self.pate else None,
            'gout': float(self.gout) if self.gout else None,
            'description': self.description,
            'photo': self.photo,
            'statut': self.statut.value if self.statut else None,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'moyenne': float(self.moyenne) if self.moyenne else None,
        }

        if include_flan:
            data['flan'] = self.flan.to_dict(include_evaluations=False)

        if include_utilisateur:
            data['utilisateur'] = self.utilisateur.to_dict()

        return data

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

    def to_dict(self):
        return {
            'id_photo': self.id_photo,
            'id_flan': self.id_flan,
            'id_etab': self.id_etab,
            'type_cible': self.type_cible.value if self.type_cible else None,
            'path': self.path,
            'largeur': self.largeur,
            'hauteur': self.hauteur,
        }
