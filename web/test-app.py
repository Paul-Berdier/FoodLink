import pytest
from app import app, db, bcrypt, Association, Commerce
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['MAIL_SUPPRESS_SEND'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_register_association(client):
    data = {
        'email': 'test@association.com',
        'password': 'password123',
        'role': 'association',
        'siret': '12345678912345',
        'nom': 'Association Test',
        'adresse': '22 rue germaine richier',
        'ville': 'Testville',
        'departement': '75',
        'tel': '0123456789'
    }
    response = client.post('/register', data=data, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Inscription r\xc3\xa9ussie' in response.data

def test_register_commerce(client):
    data = {
        'email': 'test@commerce.com',
        'password': 'password123',
        'role': 'commerce',
        'siret': '98765432109876',
        'nom': 'Commerce Test',
        'adresse': '22 rue germaine richier',
        'ville': 'Testcity',
        'departement': '34',
        'tel': '0987654321',
        'type_commerce': 'Supermarch\xc3\xa9'
    }
    response = client.post('/register', data=data, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Inscription r\xc3\xa9ussie' in response.data

def test_login(client):
    # Enregistrer un utilisateur
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    association = Association(
        nom="Login Test Association",
        adresse_mail="login@test.com",
        mdp=hashed_password,
        siret=11122233344455,
        adresse="22 rue germaine richier",
        ville="Loginville",
        departement="75",
        tel=1234567890
    )
    with app.app_context():
        db.session.add(association)
        db.session.commit()

    # Test connexion avec les bonnes informations
    response = client.post('/login', data={
        'email': 'login@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Connexion r\xc3\xa9ussie' in response.data

    # Test connexion avec un mot de passe incorrect
    response = client.post('/login', data={
        'email': 'login@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Email ou mot de passe incorrect' in response.data

    # Test connexion avec un email inexistant
    response = client.post('/login', data={
        'email': 'nonexistent@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Email ou mot de passe incorrect' in response.data

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Accueil' in response.data

def test_reset_password_request(client):
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    association = Association(
        nom="Reset Test Association",
        adresse_mail="paul.berdo@hotmail.com",
        mdp=hashed_password,
        siret=12345678912345,
        adresse="123 rue Exemple",
        ville="Exempleville",
        departement="75",
        tel=1234567890
    )
    with app.app_context():
        db.session.add(association)
        db.session.commit()

    response = client.post('/reset_password', data={
        'email': 'paul.berdo@hotmail.com'
    }, follow_redirects=True)
    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Un email de r\xc3\xa9initialisation a \xc3\xa9t\xc3\xa9 envoy\xc3\xa9' in response.data

def test_profile_update(client):
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    association = Association(
        nom="Profile Test Association",
        adresse_mail="profile@test.com",
        mdp=hashed_password,
        siret=12345678912345,
        adresse="123 rue Exemple",
        ville="Exempleville",
        departement="75",
        tel=1234567890
    )
    with app.app_context():
        db.session.add(association)
        db.session.commit()

    client.post('/login', data={
        'email': 'profile@test.com',
        'password': 'password123'
    })
    response = client.post('/profile', data={
        'email': 'updated@test.com',
        'password': 'newpassword'
    }, follow_redirects=True)

    print(response.data.decode('utf-8'))  # Debugging output
    assert response.status_code == 200
    assert b'Email mis \xc3\xa0 jour avec succ\xc3\xa8s' in response.data
    assert b'Mot de passe mis \xc3\xa0 jour avec succ\xc3\xa8s' in response.data
