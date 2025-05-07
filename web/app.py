from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from smtplib import SMTPException
from sqlalchemy.dialects.mysql import JSON
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from geocoding import get_coordinates
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_bcrypt import Bcrypt
from Register import validate_phone_number, validate_email, validate_siret
from mail_truc import envoyer_mail


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

# Dictionnaire FAQ simplifié
faq_data = {
    "qu’est-ce que foodlink": "FoodLink est une plateforme de redistribution alimentaire qui met en relation commerces, restaurants, particuliers et associations caritatives.",
    "comment créer un compte commerce": "Cliquez sur 'S’inscrire' en haut à droite, sélectionnez 'Commerce' et remplissez le formulaire.",
    "comment publier un don": "Connectez-vous à votre compte, cliquez sur 'Nouvelle offre', remplissez les infos et publiez.",
    "comment commander des produits": "Connectez-vous en tant qu’association, allez dans 'Offres disponibles', filtrez, puis cliquez sur 'Commander'.",
    "comment réinitialiser mon mot de passe": "Allez sur la page de connexion, cliquez sur 'Mot de passe oublié ?' et suivez les instructions.",
    "le site ne charge pas": "Vérifiez votre connexion ou essayez un autre navigateur. Si c’est notre serveur, une alerte s’affichera."
}

class Produit(db.Model):
    __tablename__ = 'produit'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Numeric(10, 2), nullable=False)
    marque = db.Column(db.String(50), nullable=False)


class Association(db.Model, UserMixin):
    __tablename__ = 'association'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)
    coordonnees = db.Column(JSON, nullable=True)  # Compatible MySQL
    ville = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(50), nullable=False)
    departement = db.Column(db.String(20), nullable=True)
    adresse_mail = db.Column(db.String(50), unique=True, nullable=False)  # Contrainte unique
    tel = db.Column(db.Integer, nullable=False)  # Numéros stockés comme entier (max 10 chiffres)
    siret = db.Column(db.BigInteger, nullable=False)  # Peut ajouter une validation personnalisée
    mdp = db.Column(db.String(255), nullable=False)  # Taille augmentée pour les mots de passe hashés


class Commerce(db.Model, UserMixin):
    __tablename__ = 'commerce'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)
    departement = db.Column(db.String(50), nullable=True)
    coordonnees = db.Column(JSON, nullable=True)
    type_commerce = db.Column(db.String(50), nullable=True)
    adresse = db.Column(db.String(50), nullable=False)
    ville = db.Column(db.String(50), nullable=False)
    adresse_mail = db.Column(db.String(50), unique=True, nullable=False)  # Contrainte unique
    tel = db.Column(db.Integer, nullable=False)  # Numéros stockés comme entier (max 10 chiffres)
    mdp = db.Column(db.String(255), nullable=False)
    siret = db.Column(db.BigInteger, nullable=False)


class Offre(db.Model):
    __tablename__ = 'offre'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_produit = db.Column(db.BigInteger, db.ForeignKey('produit.id', ondelete='CASCADE'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_du_lot = db.Column(db.Numeric(10, 2), nullable=False)
    date_limite = db.Column(db.Date, nullable=False)
    id_commerce = db.Column(db.BigInteger, db.ForeignKey('commerce.id', ondelete='CASCADE'), nullable=False)
    disponibilite = db.Column(db.Boolean, nullable=False, default=True)

    produit = db.relationship('Produit', backref='offres', lazy=True)
    commerce = db.relationship('Commerce', backref='offres', lazy=True)


class Echange(db.Model):
    __tablename__ = 'echange'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_offre = db.Column(db.BigInteger, db.ForeignKey('offre.id', ondelete='CASCADE'), nullable=False)
    id_association = db.Column(db.BigInteger, db.ForeignKey('association.id', ondelete='CASCADE'), nullable=False)
    date_echange = db.Column(db.Date, nullable=False)

    offre = db.relationship('Offre', backref='echanges', lazy=True)
    association = db.relationship('Association', backref='echanges', lazy=True)


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Initialisation des données pour renvoyer en cas d'erreur
    form_data = {
        "email": "",
        "role": "",
        "siret": "",
        "nom": "",
        "adresse": "",
        "ville": "",
        "departement": "",
        "tel": "",
        "type_commerce": ""
    }

    if request.method == 'POST':
        # Récupération des champs du formulaire
        form_data.update({
            "email": request.form['email'],
            "password": request.form['password'],
            "role": request.form['role'],
            "siret": request.form['siret'],
            "nom": request.form['nom'],
            "adresse": request.form['adresse'],
            "ville": request.form['ville'],
            "departement": request.form['departement'],
            "tel": request.form['tel'],
            "type_commerce": request.form.get('type_commerce', None)
        })

        # Validation des champs obligatoires
        if not all([form_data['email'], form_data['password'], form_data['role'], form_data['siret'],
                    form_data['nom'], form_data['adresse'], form_data['ville'], form_data['tel']]):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template('register.html', form_data=form_data)

        # Validation de l'adresse e-mail
        if not validate_email(form_data['email']):
            flash("L'adresse e-mail est invalide.", "danger")
            return render_template('register.html', form_data=form_data)

        # Validation de la longueur du mot de passe
        if len(form_data['password']) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
            return render_template('register.html', form_data=form_data)

        # Validation du rôle
        if form_data['role'] not in ['association', 'commerce']:
            flash("Le rôle est invalide. Choisissez 'association' ou 'commerce'.", "danger")
            return render_template('register.html', form_data=form_data)

        # Validation du numéro de téléphone
        if not validate_phone_number(form_data['tel']):
            flash("Le numéro de téléphone est invalide. Utilisez un format français valide (commençant par 0).", "danger")
            return render_template('register.html', form_data=form_data)

        # Validation du SIRET via l'API Sirene
        # try:
        #     api_url = f"https://api.insee.fr/entreprises/sirene/V3/siret/{form_data['siret']}"
        #     headers = {
        #         "Authorization": f"Bearer {os.getenv('SIREN_API_TOKEN')}"
        #     }
        #     response = requests.get(api_url, headers=headers)
        #
        #     if response.status_code != 200 or 'etablissement' not in response.json():
        #         flash("Le numéro SIRET est invalide ou introuvable.", "danger")
        #         return render_template('register.html', form_data=form_data)
        # except Exception as e:
        #     flash(f"Erreur lors de la vérification du SIRET : {str(e)}", "danger")
        #     return render_template('register.html', form_data=form_data)

        # Vérification des doublons (email ou SIRET)
        existing_user = db.session.query(Association).filter_by(adresse_mail=form_data['email']).first() or \
                        db.session.query(Commerce).filter_by(adresse_mail=form_data['email']).first()
        if existing_user:
            flash("Un compte avec cet email existe déjà.", "danger")
            return render_template('register.html', form_data=form_data)

        if db.session.query(Association).filter_by(siret=form_data['siret']).first() or \
           db.session.query(Commerce).filter_by(siret=form_data['siret']).first():
            flash("Un compte avec ce numéro SIRET existe déjà.", "danger")
            return render_template('register.html', form_data=form_data)

        # Hashage du mot de passe
        hashed_password = bcrypt.generate_password_hash(form_data['password']).decode('utf-8')

        # Création de l'utilisateur
        try:
            if form_data['role'] == 'association':
                new_user = Association(
                    nom=form_data['nom'],
                    adresse_mail=form_data['email'],
                    mdp=hashed_password,
                    siret=form_data['siret'],
                    adresse=form_data['adresse'],
                    ville=form_data['ville'],
                    departement=form_data['departement'],
                    tel=form_data['tel'],
                    coordonnees=get_coordinates(form_data['adresse'], form_data['ville'])["coordinates"]
                )
            elif form_data['role'] == 'commerce':
                new_user = Commerce(
                    nom=form_data['nom'],
                    adresse_mail=form_data['email'],
                    mdp=hashed_password,
                    siret=form_data['siret'],
                    adresse=form_data['adresse'],
                    ville=form_data['ville'],
                    departement=form_data['departement'],
                    tel=form_data['tel'],
                    coordonnees=get_coordinates(form_data['adresse'], form_data['ville'])["coordinates"],
                    type_commerce=form_data['type_commerce']
                )

            db.session.add(new_user)
            db.session.commit()
            flash('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'inscription : {str(e)}", "danger")
            return render_template('register.html', form_data=form_data)

    return render_template('register.html', form_data=form_data)

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
                message = f"Cliquez sur ce lien pour reinitialiser votre mot de passe : {reset_url}"

                envoyer_mail(email, message)
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

@app.route("/chat", methods=["POST"])


from rapidfuzz import fuzz

def is_similar(word, keywords, threshold=80):
    return any(fuzz.partial_ratio(word, kw) >= threshold for kw in keywords)

def get_response_from_article(question):
    question = question.lower()

    if is_similar(question, ["foodlink", "c'est quoi", "à propos"]):
        return """📌 Qu’est-ce que FoodLink ?

FoodLink est une plateforme de redistribution alimentaire qui met en relation **commerces, supermarchés, restaurants, particuliers** disposant de **surplus alimentaire** avec des **associations caritatives**.

Elle vise à **réduire le gaspillage alimentaire**, faciliter la logistique de redistribution et créer une chaîne solidaire locale."""

    elif is_similar(question, ["créer un compte", "inscription", "s'inscrire"]):
        return """✍️ Comment créer un compte commerce ?

1. Cliquez sur "S’inscrire" en haut à droite.
2. Choisissez “Commerce”.
3. Remplissez les infos (email, SIRET, etc.).
4. Validez et confirmez via l’email reçu."""

    elif is_similar(question, ["mot de passe", "réinitialiser", "oublié"]):
        return """🔄 Comment réinitialiser mon mot de passe ?

1. Page de connexion → “Mot de passe oublié ?”
2. Entrez votre email.
3. Suivez le lien reçu pour créer un nouveau mot de passe."""

    elif is_similar(question, ["publier", "don", "mettre un don", "ajouter un don"]):
        return """🎁 Comment publier un don ?

1. Connectez-vous à votre compte commerce.
2. Cliquez sur “Ajouter un don”.
3. Remplissez les infos (type, quantité, DLC).
4. Cliquez sur Publier."""

    elif is_similar(question, ["modifier", "offre", "changer don"]):
        return """📝 Peut-on modifier une offre après publication ?

Oui. Depuis votre tableau de bord → “Mes Offres” → Modifier."""

    elif is_similar(question, ["commander", "association", "réserver"]):
        return """🛒 Comment commander des produits ?

1. Connectez-vous avec votre compte association.
2. Allez sur “Offres disponibles”.
3. Filtrez, puis cliquez sur “Commander” ou “Réserver”."""

    elif is_similar(question, ["bug", "problème", "support", "erreur"]):
        return """🛠️ Que faire si je rencontre un bug ?

- Actualisez la page, videz le cache.
- Si ça persiste : allez dans “Support”, décrivez le bug, et l’équipe vous répondra sous 24 à 48h."""

    elif is_similar(question, ["historique", "suivre", "commande", "dons"]):
        return """🧾 Peut-on suivre l’historique des dons/commandes ?

Oui. Dans votre tableau de bord → onglet “Historique”."""

    elif is_similar(question, ["ia", "intelligence artificielle", "algorithme"]):
        return """🤖 Comment l’IA optimise les dons ?

- Prédit les futurs surplus.
- Propose les meilleures heures de collecte.
- Répartit équitablement entre associations."""

    elif is_similar(question, ["itinéraire", "trajet", "chemin"]):
        return """🗺️ Comment sont calculés les itinéraires ?

Un algorithme d’optimisation logistique choisit le trajet le plus court et le plus efficace."""

    elif is_similar(question, ["données", "confidentialité", "sécurité", "rgpd"]):
        return """🔐 Mes données sont-elles protégées ?

Oui. Données chiffrées, stockées sur serveurs sécurisés (Google Cloud), hébergées en Europe (RGPD)."""

    elif is_similar(question, ["projet", "pourquoi", "objectif"]):
        return """🌟 C’est quoi FoodLink ?

Une plateforme pour lutter contre le gaspillage alimentaire, aider les associations et valoriser les dons locaux."""

    else:
        return "❓ Désolé, je n’ai pas compris la question. Vous pouvez nous contacter à contact@foodlink.com."




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

@app.route('/entreprise', methods=['GET', 'POST'])
#@login_required
def entreprise():
    return render_template('entreprise.html')

@app.route('/association', methods=['GET', 'POST'])
#@login_required
def association():
    return render_template('association.html')

@app.route('/historique', methods=['GET', 'POST'])
#login_required
def historique():
    return render_template('historique.html')

@app.route('/aliments', methods=['GET', 'POST'])
#login_required
def aliments():
    return render_template('aliments.html')


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


if __name__ == '__main__':
    app.run(debug=True)
