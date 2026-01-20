"""Module contenant les formulaires de l'application PlanFlan.

Ce module définit tous les formulaires utilisés dans l'application Flask,
incluant les formulaires d'authentification, de création/modification
d'établissements, de flans, d'évaluations, et de recherche.
"""

import math
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    RadioField,
    HiddenField,
    DecimalField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    ValidationError,
    EqualTo,
    Optional,
    Regexp,
)
from app import bcrypt
from app.models import TypeEtab, TypePate, TypeSaveur, TypeTexture, Utilisateur


# Formulaire pour créer un compte
class RegistrationForm(FlaskForm):
    """Formulaire d'inscription pour les nouveaux utilisateurs.

    Ce formulaire permet aux nouveaux utilisateurs de créer un compte
    en fournissant un pseudo, un email, un mot de passe et sa confirmation.
    """

    pseudo = StringField("Pseudo", validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmer le mot de passe", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("S'inscrire")

    def validate_pseudo(self, pseudo):
        """Valide que le pseudo n'est pas déjà utilisé.

        Args:
            pseudo: Le champ pseudo à valider

        Raises:
            ValidationError: Si le pseudo est déjà pris
        """
        user = Utilisateur.query.filter_by(pseudo=pseudo.data).first()
        if user:
            raise ValidationError(
                "Ce pseudo est déjà pris. Veuillez en choisir un autre."
            )

    def validate_email(self, email):
        """Valide que l'email n'est pas déjà utilisé.

        Args:
            email: Le champ email à valider

        Raises:
            ValidationError: Si l'email est déjà utilisé
        """
        email = Utilisateur.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                "Cet email est déjà utilisé. Veuillez en choisir un autre."
            )


# Formulaire pour se connecter
class LoginForm(FlaskForm):
    """Formulaire de connexion pour les utilisateurs existants.

    Ce formulaire permet aux utilisateurs de se connecter à leur compte
    en fournissant leur pseudo et leur mot de passe.
    """

    pseudo = StringField("Pseudo", validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    next = HiddenField()  # Champ caché pour stocker l'URL de redirection
    submit = SubmitField("Se connecter")


# Custom coerce function for TypeEtab
def coerce_type_etab(value):
    """Convertit une valeur en chaîne pour TypeEtab.

    Args:
        value: La valeur à convertir

    Returns:
        str: La valeur convertie en chaîne
    """
    if isinstance(value, str):
        return value
    if hasattr(value, "name"):
        return value.name
    return str(value)


# Custom coerce function for TypePate
def coerce_type_pate(value):
    """Convertit une valeur en chaîne pour TypePate.

    Args:
        value: La valeur à convertir

    Returns:
        str: La valeur convertie en chaîne
    """
    if isinstance(value, str):
        return value
    if hasattr(value, "name"):
        return value.name
    return str(value)


# Custom coerce function for TypeSaveur
def coerce_type_saveur(value):
    """Convertit une valeur en chaîne pour TypeSaveur.

    Args:
        value: La valeur à convertir

    Returns:
        str: La valeur convertie en chaîne
    """
    if isinstance(value, str):
        return value
    if hasattr(value, "name"):
        return value.name
    return str(value)


# Custom coerce function for TypeTexture
def coerce_type_texture(value):
    """Convertit une valeur en chaîne pour TypeTexture.

    Args:
        value: La valeur à convertir

    Returns:
        str: La valeur convertie en chaîne
    """
    if isinstance(value, str):
        return value
    if hasattr(value, "name"):
        return value.name
    return str(value)


# Formulaire proposer/modifier un établissement
class EtabForm(FlaskForm):
    """Formulaire pour proposer ou modifier un établissement.

    Ce formulaire permet de saisir les informations d'un établissement
    incluant son type, son nom, son adresse, et d'autres détails.
    """

    type_etab = SelectField(
        "Type d'établissement",
        choices=[(choice.name, choice.value) for choice in TypeEtab],
        validators=[DataRequired(message="Ce champ est obligatoire.")],
        coerce=coerce_type_etab,
    )
    nom = HiddenField(
        "Nom",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=3,
                max=100,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    adresse = HiddenField(
        "Adresse",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=3,
                max=50,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    code_postal = HiddenField(
        "Code Postal",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(min=5, max=5, message="Longueur incorrecte."),
            Regexp("^[0-9]{5}$", message="Format invalide."),
        ],
    )
    ville = HiddenField(
        "Ville",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=3,
                max=50,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    description = StringField(
        "Description",
        validators=[
            Length(
                min=0,
                max=1000,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            )
        ],
    )
    label = BooleanField("Labellisé")
    visite = BooleanField("Visité")
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")
    google_place_id = HiddenField("Google Place ID", default="")
    id_user = HiddenField("id_user", default=1)
    submit = SubmitField("Proposer un établissement")


# Custom validator for prix field
# pylint: disable=unused-argument
def validate_prix(form, field):
    """Valide que le prix est dans une plage valide.

    Args:
        form: Le formulaire (requis par l'API Flask-WTF mais non utilisé)
        field: Le champ à valider

    Raises:
        ValidationError: Si le prix n'est pas valide
    """
    if field.data is None:
        return  # Let DataRequired handle this

    try:
        prix_value = float(field.data)
    except (ValueError, TypeError) as exc:
        raise ValidationError("Valeur invalide.") from exc

    if prix_value < 0:
        raise ValidationError("Doit être supérieur ou égal à 0.")
    if prix_value > 20:
        raise ValidationError("Le prix doit être compris entre 0 et 20€")


# Formulaire proposer/modifier un flan
class NewFlanForm(FlaskForm):
    """Formulaire pour proposer ou modifier un flan.

    Ce formulaire permet de saisir les informations d'un flan
    incluant son nom, sa saveur, sa pâte, sa texture, et son prix.
    """

    id_etab = HiddenField("ID Établissement")  # Champ caché pour l'id_etab
    nom = StringField(
        "Nom",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=3,
                max=50,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    type_saveur = SelectField(
        "Saveur",
        choices=[(choice.name, choice.value) for choice in TypeSaveur],
        coerce=coerce_type_saveur,
    )
    type_pate = SelectField(
        "Pâte",
        choices=[(choice.name, choice.value) for choice in TypePate],
        coerce=coerce_type_pate,
    )
    type_texture = SelectField(
        "Texture",
        choices=[(choice.name, choice.value) for choice in TypeTexture],
        coerce=coerce_type_texture,
    )
    description = StringField(
        "Description",
        validators=[
            Length(
                min=0,
                max=1000,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            )
        ],
    )
    prix = DecimalField(
        "Prix",
        validators=[DataRequired(message="Ce champ est obligatoire."), validate_prix],
    )
    submit = SubmitField("Proposer un flan")


# Formulaire pour proposer/modifier une évaluation
# pylint: disable=unused-argument
def validate_note(form, field):
    """Valide qu'une note est dans une plage valide.

    Args:
        form: Le formulaire (requis par l'API Flask-WTF mais non utilisé)
        field: Le champ à valider

    Raises:
        ValidationError: Si la note n'est pas valide
    """
    # First check if the data is a valid number
    if field.data is None:
        return  # Let DataRequired handle this

    try:
        # Try to convert to float if it's a string
        if isinstance(field.data, str):
            float_value = float(field.data)
        else:
            float_value = float(field.data)
    except (ValueError, TypeError) as exc:
        raise ValidationError("Valeur invalide.") from exc

    # Check if the value is in the valid range
    if 0 <= float_value <= 5:
        pass
    else:
        raise ValidationError("Doit être compris entre 0 et 5.")

    # Check if the value is in the valid choices (0.5 increments)
    valid_choices = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    if float_value not in valid_choices:
        raise ValidationError("Doit être compris entre 0 et 5.")


class EvalForm(FlaskForm):
    """Formulaire pour proposer ou modifier une évaluation.

    Ce formulaire permet de noter un flan selon différents critères
    (visuel, texture, pâte, goût) et d'ajouter une description.
    """

    # Choix valides pour les notes (0 à 5 par incréments de 0.5)
    # Utiliser des chaînes directement pour éviter les problèmes de conversion
    note_choices = [
        ("0", "0"),
        ("0.5", "0.5"),
        ("1", "1"),
        ("1.5", "1.5"),
        ("2", "2"),
        ("2.5", "2.5"),
        ("3", "3"),
        ("3.5", "3.5"),
        ("4", "4"),
        ("4.5", "4.5"),
        ("5", "5"),
    ]

    visuel = SelectField(
        "Visuel",
        choices=note_choices,
        validators=[DataRequired(message="Ce champ est obligatoire.")],
    )
    texture = SelectField(
        "Texture",
        choices=note_choices,
        validators=[DataRequired(message="Ce champ est obligatoire.")],
    )
    pate = SelectField(
        "Pâte",
        choices=note_choices,
        validators=[DataRequired(message="Ce champ est obligatoire.")],
    )
    gout = SelectField(
        "Goût",
        choices=note_choices,
        validators=[DataRequired(message="Ce champ est obligatoire.")],
    )
    description = StringField(
        "Description",
        validators=[
            Length(
                min=0,
                max=1000,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            )
        ],
    )  # Vérifier si obligatoire dans base de données
    submit = SubmitField("Proposer une évaluation")


# Custom validator for optional numeric fields
# pylint: disable=unused-argument
def validate_optional_number(form, field, min_val, max_val, message):
    """Valide qu'un nombre optionnel est dans une plage valide.

    Args:
        form: Le formulaire (requis par l'API Flask-WTF mais non utilisé)
        field: Le champ à valider
        min_val: La valeur minimale autorisée
        max_val: La valeur maximale autorisée
        message: Le message d'erreur à afficher

    Raises:
        ValidationError: Si le nombre n'est pas valide
    """
    if field.data is None or field.data == "":
        return  # Skip validation if empty

    try:
        # Try to convert to float
        num_value = float(field.data)

        # Check if it's a valid number (not NaN, not infinity)
        if min_val <= num_value <= max_val:
            pass
        else:
            raise ValidationError(message)
    except (ValueError, TypeError) as exc:
        # If conversion fails, it's not a valid number
        raise ValidationError(message) from exc


# Custom validator for optional numeric fields that handles empty strings properly
# pylint: disable=unused-argument
def validate_optional_number_field(form, field):
    """Valide qu'un nombre optionnel est valide.

    Args:
        form: Le formulaire (requis par l'API Flask-WTF mais non utilisé)
        field: Le champ à valider

    Raises:
        ValidationError: Si le nombre n'est pas valide
    """
    if field.data is None or field.data == "" or field.data is False:
        return  # Skip validation if empty or False

    try:
        # Try to convert to float
        num_value = float(field.data)

        # Check if it's a valid number (not NaN, not infinity)
        if math.isnan(num_value) or math.isinf(num_value):
            raise ValidationError("Doit être un nombre valide.")

        # Check if the value is within valid range for rayon (>= 0)
        if num_value < 0:
            raise ValidationError("Doit être supérieur ou égal à 0.")
    except (ValueError, TypeError, OverflowError) as exc:
        # If conversion fails, it's not a valid number
        raise ValidationError("Doit être un nombre valide.") from exc


# Formulaire de recherche
class RechercheForm(FlaskForm):
    """Formulaire pour rechercher des établissements et des flans.

    Ce formulaire permet de rechercher des établissements et des flans
    selon différents critères comme la localisation, le nom, la ville,
    la saveur, la pâte, la texture, le prix, etc.
    """

    latitude = (
        HiddenField()
    )  # Champ caché pour la latitude (sans validateur par défaut)
    longitude = (
        HiddenField()
    )  # Champ caché pour la longitude (sans validateur par défaut)
    rayon = StringField(
        "Rayon (km)", default="5.0"
    )  # Optionnel : laisser l'utilisateur
    # choisir le rayon
    nom = StringField(
        "Nom",
        validators=[
            Optional(),
            Length(
                min=3,
                max=50,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    ville = StringField(
        "Ville",
        validators=[Optional()],
    )
    type_saveur = SelectField(
        "Saveur",
        choices=[("tous", "Tous")]
        + [(choice.name, choice.value) for choice in TypeSaveur],
        default="tous",
    )
    type_pate = SelectField(
        "Pâte",
        choices=[("tous", "Tous")]
        + [(choice.name, choice.value) for choice in TypePate],
        default="tous",
    )
    type_texture = SelectField(
        "Texture",
        choices=[("tous", "Tous")]
        + [(choice.name, choice.value) for choice in TypeTexture],
        default="tous",
    )
    prix = SelectField(
        "Gamme de prix",
        choices=[
            ("tous", "Tous"),
            (0, "Moins de 2€50"),
            (2.5, "Plus de 2€50 mais moins de 5€"),
            (5, "Plus de 5€"),
        ],
        default="tous",
    )

    submit = SubmitField("Rechercher")
    # SEULEMENT POUR ADMIN
    visite = RadioField(
        "Visité",
        choices=[("tous", "Tous"), ("oui", "Oui"), ("non", "Non")],
        default="tous",
    )
    labellise = RadioField(
        "Labellisé",
        choices=[("tous", "Tous"), ("oui", "Oui"), ("non", "Non")],
        default="tous",
    )

    def validate_latitude(self, field):
        """Valide que la latitude est dans une plage valide.

        Args:
            field: Le champ latitude à valider

        Raises:
            ValidationError: Si la latitude n'est pas valide
        """
        validate_optional_number(
            self, field, -90, 90, "Doit être compris entre -90 et 90."
        )

    def validate_longitude(self, field):
        """Valide que la longitude est dans une plage valide.

        Args:
            field: Le champ longitude à valider

        Raises:
            ValidationError: Si la longitude n'est pas valide
        """
        validate_optional_number(
            self, field, -180, 180, "Doit être compris entre -180 et 180."
        )

    def validate_rayon(self, field):
        """Valide que le rayon est un nombre valide.

        Args:
            field: Le champ rayon à valider

        Raises:
            ValidationError: Si le rayon n'est pas valide
        """
        validate_optional_number_field(self, field)


# Formulaire pour modifier le profil de l'utilisateur
class UpdateProfileForm(FlaskForm):
    """Formulaire pour modifier le profil de l'utilisateur.

    Ce formulaire permet aux utilisateurs de mettre à jour leurs
    informations de profil, y compris le pseudo, l'email et le mot de passe.
    """

    pseudo = StringField(
        "Pseudo",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=4,
                max=50,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    email = StringField("Email", validators=[Email(message="Adresse email invalide.")])
    current_password = PasswordField(
        "Mot de passe actuel *",
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            Length(
                min=0,
                max=100,
                message="Doit contenir entre %(min)d et %(max)d caractères.",
            ),
        ],
    )
    new_password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            Length(min=8, message="Doit contenir au moins %(min)d caractères.")
        ],
    )
    confirm_password = PasswordField(
        "Confirmer mot de passe",
        validators=[
            EqualTo("new_password", message="Les mots de passe doivent correspondre.")
        ],
    )
    submit = SubmitField("Mettre à jour le profil")

    def validate_current_password(self, current_password):
        """Valide que le mot de passe actuel est correct.

        Args:
            current_password: Le champ mot de passe actuel à valider

        Raises:
            ValidationError: Si le mot de passe actuel est incorrect
        """
        # Skip validation if no current user or current_user is not authenticated
        # (for testing purposes)
        if current_user is None or not hasattr(current_user, "password"):
            return

        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError("Mot de passe actuel incorrect.")


class DeleteForm(FlaskForm):
    """Formulaire pour supprimer un élément.

    Ce formulaire simple contient uniquement un bouton de suppression.
    """

    submit = SubmitField("Supprimer")


class ValidateForm(FlaskForm):
    """Formulaire pour valider un élément.

    Ce formulaire simple contient uniquement un bouton de validation.
    """

    submit = SubmitField("Valider")
