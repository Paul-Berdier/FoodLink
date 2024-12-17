import pytest
from app import app, db, Connexion
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_register_user(client):
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Inscription r\xc3\xa9ussie" in response.data

def test_reset_password_request(client):
    with app.app_context():
        # Création d'un utilisateur test dans la base de données
        hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
        user = Connexion(
            mail_connexion="test@example.com",
            mdp_connexion=hashed_password,
            type_connexion="utilisateur",
            id_commerce="default",
            nom_commerce="default",
            departement="default",
            Id_association=1
        )
        db.session.add(user)
        db.session.commit()

    # Simulation de la demande de réinitialisation de mot de passe
    response = client.post('/reset_password', data={'email': 'test@example.com'}, follow_redirects=True)

    # Vérification du statut et du message
    assert response.status_code == 200
    assert b"Un email de r\xc3\xa9initialisation a \xc3\xa9t\xc3\xa9 envoy\xc3\xa9" in response.data
