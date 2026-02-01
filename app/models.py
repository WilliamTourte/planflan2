"""Module des modèles de données de l'application PlanFlan.

Ce module définit les modèles de base de données utilisés par l'application,
y compris les utilisateurs, les établissements, les flans et les évaluations.
Il contient également les énumérations utilisées pour typer les données.
"""

from enum import Enum
from flask_login import UserMixin
from flask import url_for
from app import db


# Enumérations
class TypeEtab(Enum):
    """Types d'établissements possibles.

    Cette énumération définit les différents types d'établissements
    qui peuvent être référencés dans l'application.
    """

    BOULANGERIE = "Boulangerie"
    PATISSERIE = "Pâtisserie"
    RESTAURANT = "Restaurant"
    CAFE = "Coffee Shop"


class StatutModeration(Enum):
    """Statuts de modération pour les établissements.

    Cette énumération définit les différents statuts que peut avoir
    un établissement dans le processus de modération.
    """

    EN_ATTENTE = "EN_ATTENTE"
    VALIDE = "VALIDE"
    SUPPRIME = "SUPPRIME"


class TypeCible(Enum):
    """Types de cibles pour les évaluations.

    Cette énumération définit les différents types de cibles
    qui peuvent être évaluées dans l'application.
    """

    FLAN = "Flan"
    ETABLISSEMENT = "Etablissement"


class TypePate(Enum):
    """Types de pâte pour les flans.

    Cette énumération définit les différents types de pâte
    qui peuvent être utilisés pour les flans.
    """

    FEUILLETEE = "Feuilletée"
    BRISEE = "Brisée"
    SUCREE = "Sucrée"
    SABLEE = "Sablée"
    MIXTE = "Mixte"


class TypeSaveur(Enum):
    """Types de saveurs pour les flans.

    Cette énumération définit les différentes saveurs
    principales des flans.
    """

    VANILLE = "Vanille"
    CHOCOLAT = "Chocolat"
    NOIX = "Noix"
    FRUITS = "Fruits"
    INSOLITE = "Insolite"
    NATURE = "Nature"


class TypeTexture(Enum):
    """Types de texture pour les flans.

    Cette énumération définit les différentes textures
    que peuvent avoir les flans.
    """

    GELATINEUSE = "Gélatineuse"
    CREMEUSE = "Crémeuse"
    FONDANTE = "Fondante"
    COSTAUD = "Costaud"
    OEUF = "Oeuf"
    MIX_PARFAIT = "Mix parfait"


# Classes base de données avec SQLAlchemy
class Utilisateur(db.Model, UserMixin):
    """Modèle représentant un utilisateur de l'application.

    Ce modèle stocke les informations des utilisateurs enregistrés,
    y compris leurs identifiants, mot de passe et rôle.
    """

    __tablename__ = "utilisateurs"
    id_user = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)

    # Relations
    etablissements = db.relationship("Etablissement", back_populates="utilisateur")
    flans = db.relationship("Flan", back_populates="utilisateur")
    evaluations = db.relationship("Evaluation", back_populates="utilisateur")

    def get_id(self):
        """Retourne l'identifiant de l'utilisateur sous forme de chaîne.

        Returns:
            str: L'identifiant de l'utilisateur
        """
        return str(self.id_user)

    def set_password(self, password, bcrypt):
        """Définit le mot de passe de l'utilisateur après hachage.

        Args:
            password (str): Le mot de passe en clair
            bcrypt: L'instance Bcrypt pour le hachage
        """
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password, bcrypt):
        """Vérifie si un mot de passe correspond au mot de passe haché.

        Args:
            password (str): Le mot de passe en clair à vérifier
            bcrypt: L'instance Bcrypt pour la vérification

        Returns:
            bool: True si le mot de passe correspond, False sinon
        """
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour la sérialisation.

        Returns:
            dict: Les données de l'utilisateur sous forme de dictionnaire
        """
        return {
            "id_user": self.id_user,
            "pseudo": self.pseudo,
            "email": self.email,
            "is_admin": self.is_admin,
            # Ne sérialise pas les relations pour éviter les boucles
            # (utilise des endpoints dédiés si besoin)
        }


from sqlalchemy import event


class Etablissement(db.Model):
    """Modèle représentant un établissement.

    Ce modèle stocke les informations des établissements où l'on peut
    trouver des flans, y compris leur localisation, leurs coordonnées
    et leur statut de modération.
    """

    __tablename__ = "etablissements"
    id_etab = db.Column(db.Integer, primary_key=True)
    type_etab = db.Column(
        db.Enum(TypeEtab), nullable=False, default=TypeEtab.BOULANGERIE
    )
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
    google_place_id = db.Column(db.String(255), nullable=True)
    statut = db.Column(
        db.Enum(StatutModeration), nullable=False, server_default="EN_ATTENTE"
    )

    # Clé étrangère pour l'utilisateur
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("utilisateurs.id_user"),
        nullable=False,
        index=True,
        server_default="1",
    )

    # Relations
    flans = db.relationship(
        "Flan", back_populates="etablissement", lazy=True, cascade="all, delete-orphan"
    )
    photos = db.relationship(
        "Photo", back_populates="etablissement", foreign_keys="Photo.id_etab"
    )
    utilisateur = db.relationship("Utilisateur", back_populates="etablissements")

    def valider_label_visite(self):
        """Valide que label ne peut être True que si visite est aussi True.

        Raises:
            ValueError: Si label est True et visite est False
        """
        if self.label and not self.visite:
            raise ValueError(
                "Un établissement ne peut être labellisé que s'il a été visité."
            )

    def to_dict(self, include_flans=True, include_photos=False):
        """Convertit l'établissement en dictionnaire pour la sérialisation.

        Args:
            include_flans (bool): Si True, inclut les flans associés
            include_photos (bool): Si True, inclut les photos associées

        Returns:
            dict: Les données de l'établissement sous forme de dictionnaire
        """
        data = {
            "id_etab": self.id_etab,
            "type_etab": self.type_etab.value if self.type_etab else None,
            "nom": self.nom,
            "adresse": self.adresse,
            "code_postal": self.code_postal,
            "ville": self.ville,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "telephone": self.telephone,
            "site_web": self.site_web,
            "description": self.description,
            "label": self.label,
            "visite": self.visite,
            "google_place_id": self.google_place_id,
            "statut": self.statut.value if self.statut else None,
            "id_user": self.id_user,
            "url": url_for("main.afficher_etablissement_unique", id_etab=self.id_etab),
        }

        if include_flans:
            data["flans"] = [
                flan.to_dict(include_etablissement=False) for flan in self.flans
            ]

        if include_photos:
            data["photos"] = [photo.to_dict() for photo in self.photos]

        return data


class Flan(db.Model):
    """Modèle représentant un flan.

    Ce modèle stocke les informations des flans proposés par les
    établissements, y compris leurs caractéristiques, leur prix
    et leur statut de modération.
    """

    __tablename__ = "flans"
    id_flan = db.Column(db.Integer, primary_key=True)
    id_etab = db.Column(
        db.Integer, db.ForeignKey("etablissements.id_etab"), nullable=False
    )
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=True)
    type_saveur = db.Column(db.Enum(TypeSaveur), nullable=True)
    type_pate = db.Column(db.Enum(TypePate), nullable=True)
    type_texture = db.Column(db.Enum(TypeTexture), nullable=True)
    statut = db.Column(
        db.Enum(StatutModeration), nullable=False, server_default="EN_ATTENTE"
    )

    # Clé étrangère pour l'utilisateur
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("utilisateurs.id_user"),
        nullable=False,
        index=True,
        default="1",
    )

    # Relations
    evaluations = db.relationship(
        "Evaluation", back_populates="flan", lazy=True, cascade="all, delete-orphan"
    )
    photos = db.relationship(
        "Photo", back_populates="flan", foreign_keys="Photo.id_flan"
    )
    etablissement = db.relationship("Etablissement", back_populates="flans")
    utilisateur = db.relationship("Utilisateur", back_populates="flans")

    def get_moyenne_evaluations(self):
        """Calcule la moyenne des évaluations pour ce flan.

        Returns:
            float: La moyenne des moyennes des évaluations, ou None si pas d'évaluations.
        """
        if not self.evaluations:
            return None

        moyennes = []

        for eval in self.evaluations:
            # Si l'évaluation a déjà une moyenne calculée, l'utiliser
            if eval.moyenne is not None:
                moyennes.append(float(eval.moyenne))
            else:
                # Calculer la moyenne à la volée si possible
                valeurs = [
                    v
                    for v in [eval.visuel, eval.texture, eval.pate, eval.gout]
                    if v is not None
                ]
                if valeurs:  # Au moins un critère est rempli
                    moyenne_calculee = sum(float(v) for v in valeurs) / len(valeurs)
                    moyennes.append(moyenne_calculee)

        if not moyennes:
            return None

        # Calculer la moyenne des moyennes
        somme = sum(moyennes)
        return round(somme / len(moyennes), 1)

    def to_dict(
        self, include_etablissement=True, include_evaluations=True, include_photos=False
    ):
        """Convertit le flan en dictionnaire pour la sérialisation.

        Args:
            include_etablissement (bool): Si True, inclut l'établissement associé
            include_evaluations (bool): Si True, inclut les évaluations associées
            include_photos (bool): Si True, inclut les photos associées

        Returns:
            dict: Les données du flan sous forme de dictionnaire
        """
        data = {
            "id_flan": self.id_flan,
            "id_etab": self.id_etab,
            "nom": self.nom,
            "description": self.description,
            "prix": float(self.prix) if self.prix else None,
            "type_saveur": self.type_saveur.value if self.type_saveur else None,
            "type_pate": self.type_pate.value if self.type_pate else None,
            "type_texture": self.type_texture.value if self.type_texture else None,
            "statut": self.statut.value if self.statut else None,
            "id_user": self.id_user,
        }

        if include_etablissement:
            data["etablissement"] = self.etablissement.to_dict(include_flans=False)

        if include_evaluations:
            data["evaluations"] = [
                eval.to_dict(include_flan=False) for eval in self.evaluations
            ]

        if include_photos:
            data["photos"] = [photo.to_dict() for photo in self.photos]

        return data



class Evaluation(db.Model):
    """Modèle représentant une évaluation.

    Ce modèle stocke les évaluations des flans faites par les
    utilisateurs, y compris les notes selon différents critères
    et les commentaires associés.
    """

    __tablename__ = "evaluations"
    __table_args__ = (
        db.UniqueConstraint("id_user", "id_flan", name="uq_user_flan_evaluation"),
    )

    id_eval = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey("utilisateurs.id_user"), nullable=False
    )
    id_flan = db.Column(db.Integer, db.ForeignKey("flans.id_flan"), nullable=False)
    visuel = db.Column(db.Numeric(2, 1), nullable=False)
    texture = db.Column(db.Numeric(2, 1), nullable=False)
    pate = db.Column(db.Numeric(2, 1), nullable=False)
    gout = db.Column(db.Numeric(2, 1), nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    statut = db.Column(
        db.Enum(StatutModeration), nullable=False, server_default="EN_ATTENTE"
    )
    date_creation = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    moyenne = db.Column(db.Numeric(2, 1), nullable=True)

    # Relations
    utilisateur = db.relationship("Utilisateur", back_populates="evaluations")
    flan = db.relationship("Flan", back_populates="evaluations")

    def calc_moyenne(self):
        """Calcule la note moyenne à partir des 4 critères d'évaluation."""
        if all(
            v is not None for v in [self.visuel, self.texture, self.pate, self.gout]
        ):
            self.moyenne = (
                float(self.visuel)
                + float(self.texture)
                + float(self.pate)
                + float(self.gout)
            ) / 4
        return self.moyenne

    def to_dict(self, include_flan=False, include_utilisateur=False):
        """Convertit l'évaluation en dictionnaire pour la sérialisation.

        Args:
            include_flan (bool): Si True, inclut le flan associé
            include_utilisateur (bool): Si True, inclut l'utilisateur associé

        Returns:
            dict: Les données de l'évaluation sous forme de dictionnaire
        """
        data = {
            "id_eval": self.id_eval,
            "id_user": self.id_user,
            "id_flan": self.id_flan,
            "visuel": float(self.visuel) if self.visuel else None,
            "texture": float(self.texture) if self.texture else None,
            "pate": float(self.pate) if self.pate else None,
            "gout": float(self.gout) if self.gout else None,
            "description": self.description,
            "photo": self.photo,
            "statut": self.statut.value if self.statut else None,
            "date_creation": (
                self.date_creation.isoformat() if self.date_creation else None
            ),
            "moyenne": float(self.moyenne) if self.moyenne else None,
        }

        if include_flan:
            data["flan"] = self.flan.to_dict(include_evaluations=False)

        if include_utilisateur:
            data["utilisateur"] = self.utilisateur.to_dict()

        return data


class Photo(db.Model):
    """Modèle représentant une photo.

    Ce modèle stocke les informations des photos associées aux
    flans ou aux établissements, y compris leur chemin,
    leurs dimensions et leur type de cible.
    """

    __tablename__ = "photos"
    id_photo = db.Column(db.Integer, primary_key=True)
    id_flan = db.Column(db.Integer, db.ForeignKey("flans.id_flan"), nullable=True)
    id_etab = db.Column(
        db.Integer, db.ForeignKey("etablissements.id_etab"), nullable=True
    )
    type_cible = db.Column(db.Enum(TypeCible), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    largeur = db.Column(db.Integer, nullable=False)
    hauteur = db.Column(db.Integer, nullable=False)

    # Relations
    etablissement = db.relationship("Etablissement", back_populates="photos")
    flan = db.relationship("Flan", back_populates="photos")

    def to_dict(self):
        """Convertit la photo en dictionnaire pour la sérialisation.

        Returns:
            dict: Les données de la photo sous forme de dictionnaire
        """
        return {
            "id_photo": self.id_photo,
            "id_flan": self.id_flan,
            "id_etab": self.id_etab,
            "type_cible": self.type_cible.value if self.type_cible else None,
            "path": self.path,
            "largeur": self.largeur,
            "hauteur": self.hauteur,
        }


# Event listeners pour nettoyer les photos orphelines
@event.listens_for(Etablissement, "before_delete")
def delete_etablissement_photos(mapper, connection, target):
    """Supprime les fichiers photos d'un établissement avant sa suppression.

    Args:
        mapper: Le mapper SQLAlchemy
        connection: La connexion à la base de données
        target: L'établissement en cours de suppression
    """
    import os
    from flask import current_app

    # Récupérer les photos associées via l'ORM (avant la suppression)
    photos = Photo.query.filter_by(id_etab=target.id_etab).all()

    for photo in photos:
        try:
            # Construire le chemin complet du fichier
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], photo.path)
            # Supprimer le fichier s'il existe
            if os.path.exists(filepath):
                os.remove(filepath)
                current_app.logger.info(f"Photo supprimée: {filepath}")
        except Exception as e:
            current_app.logger.error(
                f"Erreur lors de la suppression de la photo {photo.path}: {e}"
            )


@event.listens_for(Flan, "before_delete")
def delete_flan_photos(mapper, connection, target):
    """Supprime les fichiers photos d'un flan avant sa suppression.

    Args:
        mapper: Le mapper SQLAlchemy
        connection: La connexion à la base de données
        target: Le flan en cours de suppression
    """
    import os
    from flask import current_app

    # Récupérer les photos associées via l'ORM (avant la suppression)
    photos = Photo.query.filter_by(id_flan=target.id_flan).all()

    for photo in photos:
        try:
            # Construire le chemin complet du fichier
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], photo.path)
            # Supprimer le fichier s'il existe
            if os.path.exists(filepath):
                os.remove(filepath)
                current_app.logger.info(f"Photo supprimée: {filepath}")
        except Exception as e:
            current_app.logger.error(
                f"Erreur lors de la suppression de la photo {photo.path}: {e}"
            )

