CREATE TABLE Produit (
    id_produit VARCHAR(50),
    name_produit VARCHAR(50),
    prix DECIMAL(15,2),
    PRIMARY KEY (id_produit)
);

CREATE TABLE Association (
    Id_association INT AUTO_INCREMENT,
    nom_association VARCHAR(50),
    longitude_asso VARCHAR(50),
    latitude_asso VARCHAR(50),
    adresse_asso VARCHAR(50),
    departement_asso INT,
    adresse_mail_asso VARCHAR(50),
    num_tel_asso VARCHAR(50),
    PRIMARY KEY (Id_association)
);

CREATE TABLE Commerce (
    id_commerce VARCHAR(50),
    nom_commerce VARCHAR(50),
    departement VARCHAR(50),
    longitude_commerce VARCHAR(50),
    latitude_commerce VARCHAR(50),
    groupe VARCHAR(50),
    type_de_commerce VARCHAR(50),
    adresse_commerce VARCHAR(50),
    PRIMARY KEY (id_commerce, nom_commerce, departement)
);

CREATE TABLE Connexion (
    Id_connexion INT AUTO_INCREMENT,
    mail_connexion VARCHAR(50),
    mdp_connexion VARCHAR(255),
    type_connexion VARCHAR(50),
    id_commerce VARCHAR(50) NOT NULL,
    nom_commerce VARCHAR(50) NOT NULL,
    departement VARCHAR(50) NOT NULL,
    Id_association INT NOT NULL,
    PRIMARY KEY (Id_connexion),
    FOREIGN KEY (id_commerce, nom_commerce, departement)
        REFERENCES Commerce(id_commerce, nom_commerce, departement),
    FOREIGN KEY (Id_association)
        REFERENCES Association(Id_association)
);

CREATE TABLE Offre (
    Id_offre INT AUTO_INCREMENT,
    id_produit VARCHAR(50),
    quantite VARCHAR(50),
    prix_du_lot DECIMAL(15,2),
    date_limite DATE,
    id_commerce VARCHAR(50) NOT NULL,
    nom_commerce VARCHAR(50) NOT NULL,
    departement VARCHAR(50) NOT NULL,
    PRIMARY KEY (Id_offre, id_produit),
    FOREIGN KEY (id_commerce, nom_commerce, departement)
        REFERENCES Commerce(id_commerce, nom_commerce, departement),
    FOREIGN KEY (id_produit)
        REFERENCES Produit(id_produit)
);

CREATE TABLE Correspondre (
    id_produit VARCHAR(50),
    Id_offre INT,
    id_produit_1 VARCHAR(50),
    PRIMARY KEY (id_produit, Id_offre, id_produit_1),
    FOREIGN KEY (id_produit)
        REFERENCES Produit(id_produit),
    FOREIGN KEY (Id_offre, id_produit_1)
        REFERENCES Offre(Id_offre, id_produit)
);

CREATE TABLE Acheter (
    Id_association INT,
    Id_offre INT,
    id_produit VARCHAR(50),
    PRIMARY KEY (Id_association, Id_offre, id_produit),
    FOREIGN KEY (Id_association)
        REFERENCES Association(Id_association),
    FOREIGN KEY (Id_offre, id_produit)
        REFERENCES Offre(Id_offre, id_produit)
);
