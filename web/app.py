from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration Flask
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Configuration de SQLAlchemy pour MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialisation des extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# Modèle de la table connexion
class Connexion(db.Model):
    __tablename__ = 'connexion'
    Id_connexion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mail_connexion = db.Column(db.String(50), unique=True, nullable=False)
    mdp_connexion = db.Column(db.String(128), nullable=False)  # Haché
    type_connexion = db.Column(db.String(50), nullable=False)
    id_commerce = db.Column(db.String(50), nullable=False)
    nom_commerce = db.Column(db.String(50), nullable=False)
    departement = db.Column(db.String(50), nullable=False)
    Id_association = db.Column(db.Integer, nullable=False)

# Création des tables si elles n'existent pas
with app.app_context():
    db.create_all()

# Route d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour demander une réinitialisation de mot de passe
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = Connexion.query.filter_by(mail_connexion=email).first()
        if user:
            # Génération du jeton
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password_token', token=token, _external=True)

            # Envoi de l'email
            msg = Message(
                "Réinitialisation de votre mot de passe",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}"
            mail.send(msg)

            flash('Un email de réinitialisation a été envoyé.', 'info')
            return redirect(url_for('login'))
        else:
            flash("Adresse email inconnue.", "danger")
    return render_template('reset_password.html')

# Route pour réinitialiser le mot de passe via un jeton
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('Le lien est invalide ou expiré.', 'danger')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        user = Connexion.query.filter_by(mail_connexion=email).first()
        if user:
            user.mdp_connexion = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Votre mot de passe a été réinitialisé.', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password_token.html', email=email)

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Connexion.query.filter_by(mail_connexion=email).first()
        if user and bcrypt.check_password_hash(user.mdp_connexion, password):
            flash('Connexion réussie.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

# Route d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if Connexion.query.filter_by(mail_connexion=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = Connexion(
                mail_connexion=email,
                mdp_connexion=hashed_password,
                type_connexion='utilisateur',
                id_commerce='default_commerce',
                nom_commerce='default_name',
                departement='default_dept',
                Id_association=1
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
