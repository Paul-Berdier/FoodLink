from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import re

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmez le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Inscription')

def validate_siret(siret):
    """Vérifie si le numéro SIRET est valide (14 chiffres)."""
    return bool(re.match(r'^\d{14}$', siret))


def validate_email(email):
    """Vérifie si l'adresse e-mail a un format valide."""
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

def validate_phone_number(phone):
    """Vérifie si le numéro de téléphone français est valide."""
    return bool(re.match(r'^(?:\+33|0)[1-9](?:\d{2}){4}$', phone))
