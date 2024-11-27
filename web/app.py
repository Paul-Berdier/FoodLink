import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, flash, request
from Login import LoginForm
from Register import RegisterForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration sécurisée
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Configuration du logging
if not os.path.exists("logs"):
    os.makedirs("logs")

log_handler = RotatingFileHandler("logs/app.log", maxBytes=100000, backupCount=3)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)

# Modèle de base de données
class Connexion(db.Model):
    __tablename__ = 'connexion'
    Id_connexion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mail_connexion = db.Column(db.String(50), unique=True, nullable=False)
    mdp_connexion = db.Column(db.String(128), nullable=False)
    type_connexion = db.Column(db.String(50), nullable=False)
    id_commerce = db.Column(db.String(50), nullable=False)
    nom_commerce = db.Column(db.String(50), nullable=False)
    departement = db.Column(db.String(50), nullable=False)
    Id_association = db.Column(db.Integer, nullable=False)

# Création des tables si elles n'existent pas
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    app.logger.info('Page d\'accueil visitée')
    return render_template('index.html')

@app.route('/colaborator')
def collaborator():
    app.logger.info('Page collaborateur visitée')
    return render_template('colaborator.html')

@app.route('/association')
def collaborator():
    app.logger.info('Page association visitée')
    return render_template('association.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        app.logger.info(f'Tentative de connexion pour {form.email.data}')
        # Ajoutez la logique de vérification ici
        flash('Connexion réussie', 'success')
        return redirect(url_for('index'))
    app.logger.warning('Échec de la connexion')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        app.logger.info(f'Nouvelle inscription : {form.email.data}')
        # Ajoutez la logique d'inscription ici
        flash('Inscription réussie', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
