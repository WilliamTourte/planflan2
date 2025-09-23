from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo

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
        user = Utilisateur.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Veuillez en choisir un autre.')

# Formulaire pour se connecter
class LoginForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Se connecter')

# Formulaire pour proposer un nouvel établissement

# Formulaire pour proposer un flan

# Formulaire pour évaluer un flan