import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, flash, url_for
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer


# from models import Association, Commerce
def envoyer_mail(destinataire, message_texte):
    # Paramètres de l'expéditeur
    expediteur = "mouhcinemaimouni@gmail.com"
    mot_de_passe = "rrtk gmtx blrg teqb"  # Mot de passe d'application

    # Création du message
    message = MIMEMultipart()
    message['From'] = expediteur
    message['To'] = destinataire
    message['Subject'] = "Réinitialisation de votre mot de passe"

    print(message_texte)
    # Contenu du mail
    message.attach(MIMEText(message_texte.encode('utf-8'), 'plain', 'utf-8'))

    try:
        # Connexion au serveur SMTP de Gmail
        serveur_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        serveur_smtp.starttls()  # Activation du chiffrement TLS
        serveur_smtp.login(expediteur, mot_de_passe)  # Connexion avec les identifiants

        # Envoi du mail
        serveur_smtp.sendmail(expediteur, destinataire, message.as_string())
        print("Email envoyé avec succès !")

    except Exception as e:
        print(f"Erreur lors de l'envoi du mail : {e}")

    finally:
        serveur_smtp.quit()  # Fermeture de la connexion


