import pytest
from unittest.mock import MagicMock
from app import app, db, Connexion
from itsdangerous import URLSafeTimedSerializer

# Générateur de jetons sécurisés
s = URLSafeTimedSerializer(app.secret_key)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Accueil" in response.data


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Connexion" in response.data


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Inscription" in response.data


def test_register_user(mocker, client):
    mocker.patch('app.db.session.add', MagicMock())
    mocker.patch('app.db.session.commit', MagicMock())

    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 302  # Redirection après inscription
    assert "Inscription réussie".encode('utf-8') in response.data


def test_login_user(mocker, client):
    mock_user = Connexion(mail_connexion='test@example.com', mdp_connexion='hashedpassword')
    mocker.patch('app.Connexion.query.filter_by', return_value=MagicMock(first=lambda: mock_user))

    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirection après connexion
    assert "Connexion réussie".encode('utf-8') in response.data

def test_reset_password_request(client, mocker):
    mocker.patch('app.mail.send', MagicMock())
    mock_user = Connexion(mail_connexion='test@example.com', mdp_connexion='hashedpassword')
    mocker.patch('app.Connexion.query.filter_by', return_value=MagicMock(first=lambda: mock_user))

    response = client.post('/reset_password', data={'email': 'test@example.com'})
    assert response.status_code == 200
    assert "Un email de réinitialisation a été envoyé.".encode('utf-8') in response.data

def test_reset_password_token(client, mocker):
    email = "test@example.com"
    token = s.dumps(email, salt='password-reset-salt')

    mock_user = Connexion(mail_connexion=email, mdp_connexion='hashedpassword')
    mocker.patch('app.Connexion.query.filter_by', return_value=MagicMock(first=lambda: mock_user))

    response = client.post(f'/reset_password/{token}', data={'password': 'newpassword'})
    assert response.status_code == 200
    assert "Votre mot de passe a été réinitialisé.".encode('utf-8') in response.data

