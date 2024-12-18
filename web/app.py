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


# Modèle pour la table 'connexion'
class User(UserMixin, db.Model):
    __tablename__ = 'connexion'
    Id_connexion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mail_connexion = db.Column(db.String(50), unique=True, nullable=False)
    mdp_connexion = db.Column(db.String(128), nullable=False)
    type_connexion = db.Column(db.String(50), nullable=False, default='utilisateur')
    id_commerce = db.Column(db.String(50), nullable=False, default='default_commerce')
    nom_commerce = db.Column(db.String(50), nullable=False, default='default_name')
    departement = db.Column(db.String(50), nullable=False, default='default_dept')
    Id_association = db.Column(db.Integer, nullable=False, default=1)

    def get_id(self):
        return self.Id_connexion


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

        if User.query.filter_by(mail_connexion=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
        else:
            if len(password) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = User(
                    mail_connexion=email,
                    mdp_connexion=hashed_password,
                    type_connexion=role
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
        user = User.query.filter_by(mail_connexion=email).first()
        if user and bcrypt.check_password_hash(user.mdp_connexion, password):
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
        user = User.query.filter_by(mail_connexion=email).first()
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

    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(mail_connexion=email).first()
        if user:
            user.mdp_connexion = bcrypt.generate_password_hash(new_password).decode('utf-8')
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
        # Modification des informations
        if 'email' in request.form:
            email = request.form['email']
            if User.query.filter_by(mail_connexion=email).first() and email != user.mail_connexion:
                flash('Cet email est déjà utilisé.', 'danger')
            else:
                user.mail_connexion = email
                flash('Email mis à jour avec succès.', 'success')

        if 'password' in request.form:
            password = request.form['password']
            if len(password) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            else:
                user.mdp_connexion = bcrypt.generate_password_hash(password).decode('utf-8')
                flash('Mot de passe mis à jour avec succès.', 'success')

        if 'nom_commerce' in request.form:
            user.nom_commerce = request.form['nom_commerce']
            user.departement = request.form['departement']

        if 'nom_association' in request.form:
            association = Association.query.filter_by(Id_association=user.Id_association).first()
            if association:
                association.nom_association = request.form['nom_association']
                association.adresse_asso = request.form['adresse_asso']
                association.num_tel_asso = request.form['num_tel_asso']
                db.session.commit()
                flash("Les informations de l'association ont été mises à jour.", "success")

        db.session.commit()

    return render_template('profile.html', user=user)



if __name__ == '__main__':
    app.run(debug=True)
