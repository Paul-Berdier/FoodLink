CREATE DATABASE IF NOT EXISTS FoodLink;

USE FoodLink;

-- Création de la table 'produit'
CREATE TABLE IF NOT EXISTS produit(
   id BIGINT,  -- Changement du type de NUMERIC à BIGINT
   nom VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL pour imposer la présence d'un nom
   prix DECIMAL(10,2) NOT NULL,  -- Changement de NUMERIC à DECIMAL pour une meilleure gestion des prix
   marque VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL pour la marque
   PRIMARY KEY(id)
);

-- Création de la table 'association'
CREATE TABLE IF NOT EXISTS association (
    id BIGINT,  -- Changement de NUMERIC à BIGINT
    nom VARCHAR(50) NOT NULL,  -- Augmentation de la longueur et ajout de NOT NULL
    coordonnees JSON,
    ville VARCHAR(50) NOT NULL,  -- Longueur augmentée pour 'ville' et ajout de NOT NULL
    adresse VARCHAR(50) NOT NULL,  -- Longueur augmentée pour 'adresse'
    departement VARCHAR(20),  -- Change NUMERIC en INT pour plus de précision
    adresse_mail VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL
    tel VARCHAR(20),
    siret BIGINT NOT NULL,  -- Changement de INT à BIGINT pour siret
    mdp VARCHAR(50) NOT NULL,  -- Augmentation de la longueur pour les mots de passe
    PRIMARY KEY(id)
);

-- Création de la table 'commerce'
CREATE TABLE IF NOT EXISTS commerce (
   id BIGINT,  -- Changement de NUMERIC à BIGINT
   nom VARCHAR(50) NOT NULL,  -- Augmentation de la longueur et ajout de NOT NULL
   departement VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL
   coordonnees JSON,  -- Le type JSON reste inchangé
   type_commerce VARCHAR(50) NOT NULL,  -- Ajout de NOT NULL pour la présence du type
   adresse VARCHAR(50) NOT NULL,  -- Longueur augmentée
   ville VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL
   adresse_mail VARCHAR(50) NOT NULL,  -- Longueur augmentée et ajout de NOT NULL
   tel VARCHAR(20),
    mdp VARCHAR(50) NOT NULL,
   siret BIGINT NOT NULL,  -- Changement de INT à BIGINT pour siret
   PRIMARY KEY(id)
);

-- Création de la table 'offre'
CREATE TABLE IF NOT EXISTS offre (
    id BIGINT ,  -- Changement de NUMERIC à BIGINT
    id_produit BIGINT NOT NULL,  -- Correspondance avec le type de la clé étrangère
    quantite INT(3) NOT NULL,  -- Ajout de NOT NULL
    prix_du_lot DECIMAL(10,2) NOT NULL,  -- Changement de NUMERIC à DECIMAL pour une gestion des prix plus précise
    date_limite DATE NOT NULL,  -- Ajout de NOT NULL
    id_commerce BIGINT NOT NULL,  -- Correspondance avec le type de la clé étrangère
    disponibilite BOOLEAN NOT NULL,  -- Ajout de NOT NULL pour la disponibilité
    PRIMARY KEY(id),
    FOREIGN KEY (id_commerce) REFERENCES commerce(id) ON DELETE CASCADE,
    FOREIGN KEY (id_produit) REFERENCES produit(id) ON DELETE CASCADE
);

-- Création de la table 'echange'
CREATE TABLE IF NOT EXISTS echange (
    id BIGINT ,  -- Changement de NUMERIC à BIGINT
    id_offre BIGINT NOT NULL,  -- Correspondance avec le type de la clé étrangère
    id_association BIGINT NOT NULL,  -- Correspondance avec le type de la clé étrangère
    date_echange DATE NOT NULL,  -- Ajout de NOT NULL pour la date
    PRIMARY KEY(id),
    FOREIGN KEY (id_association) REFERENCES association(id) ON DELETE CASCADE,
    FOREIGN KEY (id_offre) REFERENCES offre(id) ON DELETE CASCADE
);
