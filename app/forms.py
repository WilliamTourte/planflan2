from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    pseudo = StringField('Pseudo', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Se connecter')
