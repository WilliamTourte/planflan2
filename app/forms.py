

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField, HiddenField, \
    DecimalField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo, NumberRange
from app.models import TypeEtab

from app.models import Utilisateur

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

# Formulaire pour proposer un nouvel établissement
class EtabForm(FlaskForm):
    type_etab = SelectField("Type d'établissement", choices=TypeEtab, validators=[DataRequired()]  )
    nom = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    adresse = StringField('Adresse', validators=[DataRequired(), Length(min=3, max=50)])
    code_postal = StringField('Code Postal', validators=[DataRequired(), Length(min=5, max=5)])
    ville = StringField('Ville', validators=[DataRequired(), Length(min=3, max=50)])

    description = StringField('Description', validators=[ Length(min=3, max=255)]) #Vérifier si obligatoire dans base de données
    label = RadioField('Labellisé', choices=[('Oui','Labellisé par la Flanterie'),('Non','Non labellisé')])
    visite = RadioField('Visité', choices=[('Oui','Visité par la Flanterie'),('Non','Non visité')])
    submit = SubmitField('Proposer un établissement')


# Formulaire pour proposer un flan dans un établissement déjà ajouté
class NewFlanForm(FlaskForm):
    id_etab = HiddenField('ID Établissement')  # Champ caché pour l'id_etab
    nom = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    description = StringField('Description', validators=[Length(min=3, max=255)])
    prix = DecimalField('Prix', validators=[DataRequired(), NumberRange(0,20, "Le prix doit être compris entre 0 et 20€") ])

    submit = SubmitField('Proposer un flan')


# Formulaire pour évaluer un flan
class EvalForm(FlaskForm):
    visuel = SelectField("Visuel", choices=[(0,0), (0.5,0.5), (1,1),(1.5,1.5),(2,2),(2.5,2.5),(3,3),(3.5,3.5),(4,4),(4.5,4.5),(5,5)], validators=[DataRequired()] )
    texture =SelectField("Texture", choices=[(0,0), (0.5,0.5), (1,1),(1.5,1.5),(2,2),(2.5,2.5),(3,3),(3.5,3.5),(4,4),(4.5,4.5),(5,5)], validators=[DataRequired()] )
    pate = SelectField("Pâte", choices=[(0,0), (0.5,0.5), (1,1),(1.5,1.5),(2,2),(2.5,2.5),(3,3),(3.5,3.5),(4,4),(4.5,4.5),(5,5)], validators=[DataRequired()] )
    gout = SelectField("Goût", choices=[(0,0), (0.5,0.5), (1,1),(1.5,1.5),(2,2),(2.5,2.5),(3,3),(3.5,3.5),(4,4),(4.5,4.5),(5,5)], validators=[DataRequired()] )
    description = StringField('Description', validators=[Length(min=3, max=255)]) #Vérifier si obligatoire dans base de données

# Formulaire pour rechercher un établissement
class ChercheEtabForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Rechercher')

