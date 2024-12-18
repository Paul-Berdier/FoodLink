from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from smtplib import SMTPException
import os

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration Flask
app.secret_key = os.getenv('FLASK_SECRET_KEY')
s = URLSafeTimedSerializer(app.secret_key)

# Configuration SQLAlchemy pour MySQL
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
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

# Configuration Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Modèles pour les nouvelles tables
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    prix = db.Column(db.Float, nullable=False)
    marque = db.Column(db.Text, nullable=True)


class Association(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    coordonnees = db.Column(db.Text, nullable=True)
    ville = db.Column(db.Text, nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    departement = db.Column(db.Integer, nullable=True)
    adresse_mail = db.Column(db.Text, unique=True, nullable=False)
    tel = db.Column(db.Text, nullable=True)
    siret = db.Column(db.Text, nullable=False)
    mdp = db.Column(db.Text, nullable=False)


class Commerce(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=False)
    departement = db.Column(db.Text, nullable=True)
    coordonnees = db.Column(db.Text, nullable=True)
    type_commerce = db.Column(db.Text, nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    ville = db.Column(db.Text, nullable=True)
    adresse_mail = db.Column(db.Text, unique=True, nullable=False)
    tel = db.Column(db.Text, nullable=True)
    siret = db.Column(db.Text, nullable=False)
    mdp = db.Column(db.Text, nullable=False)


class Offre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_produit = db.Column(db.Integer, db.ForeignKey("produit.id"), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_du_lot = db.Column(db.Float, nullable=False)
    date_limite = db.Column(db.DateTime, nullable=False)
    id_commerce = db.Column(db.Integer, db.ForeignKey("commerce.id"), nullable=False)
    disponibilite = db.Column(db.Boolean, default=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_offre = db.Column(db.Integer, db.ForeignKey("offre.id"), nullable=False)
    id_association = db.Column(db.Integer, db.ForeignKey("association.id"), nullable=False)
    date_transaction = db.Column(db.DateTime, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    user = Association.query.get(int(user_id))
    if not user:
        user = Commerce.query.get(int(user_id))
    return user


# Création des tables si elles n'existent pas
with app.app_context():
    db.create_all()


# Route d'accueil
@app.route('/')
def index():
    return render_template('index.html')


# Route d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        siret = request.form['siret']

        if role == 'association':
            if Association.query.filter_by(adresse_mail=email).first():
                flash('Cet email est déjà utilisé.', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = Association(
                    adresse_mail=email,
                    mdp=hashed_password,
                    siret=siret,
                    nom=request.form['nom']
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('login'))

        elif role == 'commerce':
            if Commerce.query.filter_by(adresse_mail=email).first():
                flash('Cet email est déjà utilisé.', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = Commerce(
                    adresse_mail=email,
                    mdp=hashed_password,
                    siret=siret,
                    nom=request.form['nom']
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('login'))
    return render_template('register.html')


# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Association.query.filter_by(adresse_mail=email).first()
        if not user:
            user = Commerce.query.filter_by(adresse_mail=email).first()

        if user and bcrypt.check_password_hash(user.mdp, password):
            login_user(user)
            flash('Connexion réussie.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login.html')


# Route de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))


# Route pour demander une réinitialisation de mot de passe
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = Association.query.filter_by(adresse_mail=email).first()
        if not user:
            user = Commerce.query.filter_by(adresse_mail=email).first()

        if user:
            try:
                token = s.dumps(email, salt='password-reset-salt')
                reset_url = url_for('reset_password_token', token=token, _external=True)
                msg = Message(
                    "Réinitialisation de votre mot de passe",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email]
                )
                msg.body = f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}"
                mail.send(msg)
                flash('Un email de réinitialisation a été envoyé.', 'info')
            except SMTPException:
                flash("Erreur lors de l'envoi de l'email. Veuillez réessayer plus tard.", 'danger')
        else:
            flash("Adresse email inconnue.", "danger")
    return render_template('reset_password.html')


# Route pour réinitialiser le mot de passe via un token
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('Le lien est invalide ou expiré.', 'danger')
        return redirect(url_for('reset_password'))

    user = Association.query.filter_by(adresse_mail=email).first()
    if not user:
        user = Commerce.query.filter_by(adresse_mail=email).first()

    if request.method == 'POST':
        new_password = request.form['password']
        if len(new_password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
        else:
            user.mdp = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Votre mot de passe a été réinitialisé.', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password_token.html', email=email)


# Route pour afficher et modifier les informations du profil
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    if request.method == 'POST':
        # Modification des informations utilisateur
        if 'email' in request.form:
            email = request.form['email']
            if (Association.query.filter_by(adresse_mail=email).first() or
                    Commerce.query.filter_by(adresse_mail=email).first()) and email != user.adresse_mail:
                flash('Cet email est déjà utilisé.', 'danger')
            else:
                user.adresse_mail = email
                flash('Email mis à jour avec succès.', 'success')

        if 'password' in request.form:
            password = request.form['password']
            if len(password) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            else:
                user.mdp = bcrypt.generate_password_hash(password).decode('utf-8')
                flash('Mot de passe mis à jour avec succès.', 'success')

        if isinstance(user, Commerce):
            if 'nom' in request.form:
                user.nom = request.form['nom']
            if 'adresse' in request.form:
                user.adresse = request.form['adresse']
            if 'ville' in request.form:
                user.ville = request.form['ville']
            if 'tel' in request.form:
                user.tel = request.form['tel']

        elif isinstance(user, Association):
            if 'nom' in request.form:
                user.nom = request.form['nom']
            if 'adresse' in request.form:
                user.adresse = request.form['adresse']
            if 'ville' in request.form:
                user.ville = request.form['ville']
            if 'tel' in request.form:
                user.tel = request.form['tel']

        db.session.commit()

    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
