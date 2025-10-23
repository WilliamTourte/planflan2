from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField, HiddenField, \
    DecimalField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo, NumberRange, Optional
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

# Formulaire proposer/modifier un établissement
class EtabForm(FlaskForm):
    type_etab = SelectField("Type d'établissement", choices=[(choice.name, choice.value) for choice in TypeEtab],
                          validators=[DataRequired()])
    nom = HiddenField('Nom', validators=[DataRequired(), Length(min=3, max=100)])
    adresse = HiddenField('Adresse', validators=[DataRequired(), Length(min=3, max=50)])
    code_postal = HiddenField('Code Postal', validators=[DataRequired(), Length(min=5, max=5)])
    ville = HiddenField('Ville', validators=[DataRequired(), Length(min=3, max=50)])
    description = StringField('Description', validators=[Length(min=3, max=255)])
    label = BooleanField('Labellisé')
    visite = BooleanField('Visité')
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    submit = SubmitField('Proposer un établissement')

# Formulaire proposer/modifier un flan
class NewFlanForm(FlaskForm):
    id_etab = HiddenField('ID Établissement')  # Champ caché pour l'id_etab
    nom = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    type_saveur = SelectField('Saveur', choices=[(choice.name, choice.value) for choice in TypeSaveur])
    type_pate = SelectField('Pâte',  choices=[(choice.name, choice.value) for choice in TypePate])
    type_texture = SelectField('Texture',  choices=[(choice.name, choice.value) for choice in TypeTexture])
    description = StringField('Description', validators=[Length(min=3, max=255)])
    prix = DecimalField('Prix', validators=[DataRequired(), NumberRange(0,20, "Le prix doit être compris entre 0 et 20€") ])
    submit = SubmitField('Proposer un flan')

# Formulaire pour proposer/modifier une évaluation
class EvalForm(FlaskForm):
    choix=[(0,0), (0.5,0.5), (1,1),(1.5,1.5),(2,2),(2.5,2.5),(3,3),(3.5,3.5),(4,4),(4.5,4.5),(5,5)]
    visuel = SelectField("Visuel", choices=choix, validators=[DataRequired()] )
    texture =SelectField("Texture", choices=choix, validators=[DataRequired()] )
    pate = SelectField("Pâte", choices=choix, validators=[DataRequired()] )
    gout = SelectField("Goût", choices=choix, validators=[DataRequired()] )
    description = StringField('Description', validators=[Length(min=3, max=255)]) #Vérifier si obligatoire dans base de données
    submit = SubmitField('Proposer une évaluation')

# Formulaire de recherche
class RechercheForm(FlaskForm):
    nom = StringField('Nom', validators=[Optional(), Length(min=3, max=50)])
    ville = StringField('Ville', validators=[Optional(), Length(min=3, max=50)])
    type_saveur = SelectField('Saveur', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypeSaveur], default='tous')
    type_pate = SelectField('Pâte', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypePate], default='tous')
    type_texture = SelectField('Texture', choices=[('tous', 'Tous')] + [(choice.name, choice.value) for choice in TypeTexture], default='tous')
    prix = prix = SelectField('Gamme de prix', choices=[('tous', 'Tous'), (0, "Moins de 2€50"), (2.5, "Plus de 2€50 mais moins de 5€"), (5, "Plus de 5€")], default='tous')

    submit = SubmitField('Rechercher')
    # SEULEMENT POUR ADMIN #
    visite = RadioField('Visité', choices=[('tous', 'Tous'), ('oui', 'Oui'), ('non', 'Non')], default='tous')
    labellise = RadioField('Labellisé', choices=[('tous', 'Tous'), ('oui', 'Oui'), ('non', 'Non')], default='tous')

# Formulaire pour modifier le profil de l'utilisateur
class UpdateProfileForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[Optional(), Length(min=4, max=50)])
    email = StringField('Email', validators=[Optional(), Email()])
    current_password = PasswordField('Mot de passe actuel *', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[Optional(), EqualTo('confirm_password'), Length(min=6)])
    confirm_password = PasswordField('Confirmer mot de passe', validators=[Optional()])
    submit = SubmitField('Mettre à jour le profil')

    def validate_current_password(self, current_password):
        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError('Current password is incorrect.')

