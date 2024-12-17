from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

# Fonction pour vérifier la complexité du mot de passe
def strong_password(form, field):
    password = field.data
    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        raise ValidationError('Le mot de passe doit contenir au moins 8 caractères, une majuscule et un chiffre.')

class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Adresse e-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), strong_password])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Rôle", choices=[('user', 'Utilisateur'), ('admin', 'Administrateur'), ('moderator', 'Modérateur')])
    submit = SubmitField("S'inscrire")
