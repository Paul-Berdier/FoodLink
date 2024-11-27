from flask import Flask, render_template, redirect, url_for, flash, request
from Login import LoginForm
from Register import RegisterForm

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Ceci est encore nécessaire pour `flash` et les sessions.

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        # Ajoutez la logique de vérification ici sans CSRF
        flash('Connexion réussie', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        # Ajoutez la logique d'inscription ici sans CSRF
        flash('Inscription réussie', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
