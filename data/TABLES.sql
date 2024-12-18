CREATE DATABASE IF NOT EXISTS FoodLink;

USE FoodLink;

CREATE TABLE IF NOT EXISTS produit(
   id NUMERIC,
   nom TEXT,
   prix NUMERIC,
   marque TEXT,
   PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS association (
    id NUMERIC,
    nom TEXT,
    coordonnees TEXT,
    ville TEXT,
    adresse TEXT,
    departement NUMERIC,
    adresse_mail TEXT,
    tel TEXT,
    siret TEXT,
    mdp TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS commerce (
   id NUMERIC,
   nom TEXT,
   departement TEXT,
   coordonnees TEXT,
   type_commerce TEXT,
   adresse TEXT,
   ville TEXT,
   adresse_mail TEXT,
   tel TEXT,
   siret TEXT,
   PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS offre (
    id NUMERIC,
    id_produit NUMERIC,
    quantite NUMERIC,
    prix_du_lot NUMERIC,
    date_limite DATETIME,
    id_commerce NUMERIC,
    disponibilite BOOLEAN,
    PRIMARY KEY(id),
    FOREIGN KEY (id_commerce) REFERENCES commerce(id),
    FOREIGN KEY (id_produit) REFERENCES produit(id)
);

CREATE TABLE IF NOT EXISTS `transaction` (
    id NUMERIC,
    id_offre NUMERIC,
    id_association NUMERIC,
    date_transaction DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (id_association) REFERENCES association(id),
    FOREIGN KEY (id_offre) REFERENCES offre(id)
);
