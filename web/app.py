from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request
from Login import LoginForm
from Register import RegisterForm
import os

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv('FLASK_CODE')


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/colaborator')
def collaborator():
    return redirect(url_for('colaborator.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Ajoutez la logique de vérification ici
        flash('Connexion réussie', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Ajoutez la logique d'inscription ici
        flash('Inscription réussie', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
