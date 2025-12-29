import math
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField, HiddenField, \
    DecimalField, FloatField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo, NumberRange, Optional, Regexp
from app import bcrypt
from app.models import TypeEtab, TypePate, TypeSaveur, TypeTexture, Utilisateur

# Formulaire pour créer un compte
class RegistrationForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                    validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Administrateur')
    submit = SubmitField("S'inscrire")

    def validate_pseudo(self, pseudo):
        user = Utilisateur.query.filter_by(pseudo=pseudo.data).first()
        if user:
            raise ValidationError('Ce pseudo est déjà pris. Veuillez en choisir un autre.')

    def validate_email(self, email):
        email = Utilisateur.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')

# Formulaire pour se connecter
class LoginForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    next = HiddenField()  # Champ caché pour stocker l'URL de redirection
    submit = SubmitField('Se connecter')

# Custom coerce function for TypeEtab
def coerce_type_etab(value):
    if isinstance(value, str):
        return value
    elif hasattr(value, 'name'):
        return value.name
    else:
        return str(value)

# Custom coerce function for TypePate
def coerce_type_pate(value):
    if isinstance(value, str):
        return value
    elif hasattr(value, 'name'):
        return value.name
    else:
        return str(value)

# Custom coerce function for TypeSaveur
def coerce_type_saveur(value):
    if isinstance(value, str):
        return value
    elif hasattr(value, 'name'):
        return value.name
    else:
        return str(value)

# Custom coerce function for TypeTexture
def coerce_type_texture(value):
    if isinstance(value, str):
        return value
    elif hasattr(value, 'name'):
        return value.name
    else:
        return str(value)

# Formulaire proposer/modifier un établissement
class EtabForm(FlaskForm):
    type_etab = SelectField("Type d'établissement", choices=[(choice.name, choice.value) for choice in TypeEtab],
                          validators=[DataRequired(message='Ce champ est obligatoire.')], coerce=coerce_type_etab)
    nom = HiddenField('Nom', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=3, max=100, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    adresse = HiddenField('Adresse', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=3, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    code_postal = HiddenField('Code Postal', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=5, max=5, message='Longueur incorrecte.'), Regexp('^[0-9]{5}$', message='Format invalide.')])
    ville = HiddenField('Ville', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=3, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    description = StringField('Description', validators=[Length(min=0, max=1000, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    label = BooleanField('Labellisé')
    visite = BooleanField('Visité')
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    id_user = HiddenField('id_user', default=1)
    submit = SubmitField('Proposer un établissement')

# Custom validator for prix field
def validate_prix(form, field):
    if field.data is None:
        return  # Let DataRequired handle this
    
    try:
        prix_value = float(field.data)
    except (ValueError, TypeError):
        raise ValidationError('Valeur invalide.')
    
    if prix_value < 0:
        raise ValidationError('Doit être supérieur ou égal à 0.')
    elif prix_value > 20:
        raise ValidationError('Le prix doit être compris entre 0 et 20€')

# Formulaire proposer/modifier un flan
class NewFlanForm(FlaskForm):
    id_etab = HiddenField('ID Établissement')  # Champ caché pour l'id_etab
    nom = StringField('Nom', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=3, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    type_saveur = SelectField('Saveur', choices=[(choice.name, choice.value) for choice in TypeSaveur], coerce=coerce_type_saveur)
    type_pate = SelectField('Pâte',  choices=[(choice.name, choice.value) for choice in TypePate], coerce=coerce_type_pate)
    type_texture = SelectField('Texture',  choices=[(choice.name, choice.value) for choice in TypeTexture], coerce=coerce_type_texture)
    description = StringField('Description', validators=[Length(min=0, max=1000, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    prix = DecimalField('Prix', validators=[DataRequired(message='Ce champ est obligatoire.'), validate_prix])
    submit = SubmitField('Proposer un flan')

# Formulaire pour proposer/modifier une évaluation
def validate_note(form, field):
    # First check if the data is a valid number
    if field.data is None:
        return  # Let DataRequired handle this
    
    try:
        # Try to convert to float if it's a string
        if isinstance(field.data, str):
            float_value = float(field.data)
        else:
            float_value = float(field.data)
    except (ValueError, TypeError):
        raise ValidationError('Valeur invalide.')
    
    # Check if the value is in the valid range
    if not (0 <= float_value <= 5):
        raise ValidationError('Doit être compris entre 0 et 5.')
    
    # Check if the value is in the valid choices (0.5 increments)
    valid_choices = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    if float_value not in valid_choices:
        raise ValidationError('Doit être compris entre 0 et 5.')

class EvalForm(FlaskForm):
    visuel = FloatField("Visuel", validators=[DataRequired(message='Ce champ est obligatoire.'), validate_note] )
    texture = FloatField("Texture", validators=[DataRequired(message='Ce champ est obligatoire.'), validate_note] )
    pate = FloatField("Pâte", validators=[DataRequired(message='Ce champ est obligatoire.'), validate_note] )
    gout = FloatField("Goût", validators=[DataRequired(message='Ce champ est obligatoire.'), validate_note] )
    description = StringField('Description', validators=[Length(min=0, max=1000, message='Doit contenir entre %(min)d et %(max)d caractères.')]) #Vérifier si obligatoire dans base de données
    submit = SubmitField('Proposer une évaluation')

# Custom validator for optional numeric fields
def validate_optional_number(form, field, min_val, max_val, message):
    if field.data is None or field.data == '':
        return  # Skip validation if empty
    
    try:
        # Try to convert to float
        num_value = float(field.data)
        
        # Check if it's a valid number (not NaN, not infinity)
        if not (min_val <= num_value <= max_val):
            raise ValidationError(message)
    except (ValueError, TypeError):
        # If conversion fails, it's not a valid number
        raise ValidationError(message)

# Custom validator for optional numeric fields that handles empty strings properly
def validate_optional_number_field(form, field):
    if field.data is None or field.data == '' or field.data is False:
        return  # Skip validation if empty or False
    
    try:
        # Try to convert to float
        num_value = float(field.data)
        
        # Check if it's a valid number (not NaN, not infinity)
        if math.isnan(num_value) or math.isinf(num_value):
            raise ValidationError('Doit être un nombre valide.')
        
        # Check if the value is within valid range for rayon (>= 0)
        if num_value < 0:
            raise ValidationError('Doit être supérieur ou égal à 0.')
    except (ValueError, TypeError, OverflowError):
        # If conversion fails, it's not a valid number
        raise ValidationError('Doit être un nombre valide.')

# Formulaire de recherche
class RechercheForm(FlaskForm):
    latitude = HiddenField()  # Champ caché pour la latitude (sans validateur par défaut)
    longitude = HiddenField()  # Champ caché pour la longitude (sans validateur par défaut)
    rayon = StringField('Rayon (km)', default='5.0')  # Optionnel : laisser l'utilisateur choisir le rayon
    nom = StringField('Nom', validators=[Optional(), Length(min=3, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    ville = StringField('Ville', validators=[Optional(), Length(min=3, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    type_saveur = SelectField('Saveur', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypeSaveur], default='tous')
    type_pate = SelectField('Pâte', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypePate], default='tous')
    type_texture = SelectField('Texture', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypeTexture], default='tous')
    prix = prix = SelectField('Gamme de prix', choices=[('tous', 'Tous'), (0, "Moins de 2€50"), (2.5, "Plus de 2€50 mais moins de 5€"), (5, "Plus de 5€")], default='tous')

    submit = SubmitField('Rechercher')
    # SEULEMENT POUR ADMIN #
    visite = RadioField('Visité', choices=[('tous', 'Tous'), ('oui', 'Oui'), ('non', 'Non')], default='tous')
    labellise = RadioField('Labellisé', choices=[('tous', 'Tous'), ('oui', 'Oui'), ('non', 'Non')], default='tous')
    
    def validate_latitude(form, field):
        validate_optional_number(form, field, -90, 90, 'Doit être compris entre -90 et 90.')
    
    def validate_longitude(form, field):
        validate_optional_number(form, field, -180, 180, 'Doit être compris entre -180 et 180.')
    
    def validate_rayon(form, field):
        validate_optional_number_field(form, field)

# Formulaire pour modifier le profil de l'utilisateur
class UpdateProfileForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=4, max=50, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    email = StringField('Email', validators=[Email(message='Adresse email invalide.')])
    current_password = PasswordField('Mot de passe actuel *', validators=[DataRequired(message='Ce champ est obligatoire.'), Length(min=0, max=100, message='Doit contenir entre %(min)d et %(max)d caractères.')])
    new_password = PasswordField('Nouveau mot de passe', validators=[Length(min=8, message='Doit contenir au moins %(min)d caractères.')])
    confirm_password = PasswordField('Confirmer mot de passe', validators=[EqualTo('new_password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField('Mettre à jour le profil')

    def validate_current_password(self, current_password):
        # Skip validation if no current user or current_user is not authenticated (for testing purposes)
        if current_user is None or not hasattr(current_user, 'password'):
            return
            
        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError('Mot de passe actuel incorrect.')

class DeleteForm(FlaskForm):
        submit = SubmitField('Supprimer')

class ValidateForm(FlaskForm):
        submit = SubmitField('Valider')