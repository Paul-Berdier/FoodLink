CREATE DATABASE IF NOT EXISTS FoodLink;

USE FoodLink;

-- Création de la table 'produit'
CREATE TABLE IF NOT EXISTS produit (
    id BIGINT AUTO_INCREMENT,  -- Ajout d'AUTO_INCREMENT pour générer automatiquement les IDs
    nom VARCHAR(50) NOT NULL,  -- Le nom est obligatoire
    prix DECIMAL(10,2) NOT NULL,  -- Gestion précise des prix
    marque VARCHAR(50) NOT NULL,  -- La marque est obligatoire
    PRIMARY KEY (id)  -- Définition de la clé primaire
);

-- Création de la table 'association'
CREATE TABLE IF NOT EXISTS association (
    id BIGINT AUTO_INCREMENT,  -- Ajout d'AUTO_INCREMENT pour générer automatiquement les IDs
    nom VARCHAR(50) NOT NULL,  -- Le nom est obligatoire
    coordonnees JSON,  -- Les coordonnées en format JSON
    ville VARCHAR(50) NOT NULL,  -- La ville est obligatoire
    adresse VARCHAR(50) NOT NULL,  -- L'adresse est obligatoire
    departement VARCHAR(20),  -- Département (optionnel)
    adresse_mail VARCHAR(50) NOT NULL UNIQUE,  -- Adresse email unique et obligatoire
    tel VARCHAR(20),  -- Numéro de téléphone (optionnel)
    siret BIGINT NOT NULL,  -- SIRET obligatoire
    mdp VARCHAR(50) NOT NULL,  -- Mot de passe obligatoire
    PRIMARY KEY (id)  -- Définition de la clé primaire
);

-- Création de la table 'commerce'
CREATE TABLE IF NOT EXISTS commerce (
    id BIGINT AUTO_INCREMENT,  -- Ajout d'AUTO_INCREMENT pour générer automatiquement les IDs
    nom VARCHAR(50) NOT NULL,  -- Le nom est obligatoire
    departement VARCHAR(50) NOT NULL,  -- Le département est obligatoire
    coordonnees JSON,  -- Les coordonnées en format JSON
    type_commerce VARCHAR(50) NOT NULL,  -- Type de commerce obligatoire
    adresse VARCHAR(50) NOT NULL,  -- L'adresse est obligatoire
    ville VARCHAR(50) NOT NULL,  -- La ville est obligatoire
    adresse_mail VARCHAR(50) NOT NULL UNIQUE,  -- Adresse email unique et obligatoire
    tel VARCHAR(20),  -- Numéro de téléphone (optionnel)
    mdp VARCHAR(50) NOT NULL,  -- Mot de passe obligatoire
    siret BIGINT NOT NULL,  -- SIRET obligatoire
    PRIMARY KEY (id)  -- Définition de la clé primaire
);

-- Création de la table 'offre'
CREATE TABLE IF NOT EXISTS offre (
    id BIGINT AUTO_INCREMENT,  -- Ajout d'AUTO_INCREMENT pour générer automatiquement les IDs
    id_produit BIGINT NOT NULL,  -- Référence au produit
    quantite INT NOT NULL,  -- Quantité obligatoire
    prix_du_lot DECIMAL(10,2) NOT NULL,  -- Gestion précise des prix
    date_limite DATE NOT NULL,  -- Date limite obligatoire
    id_commerce BIGINT NOT NULL,  -- Référence au commerce
    disponibilite BOOLEAN NOT NULL,  -- Disponibilité obligatoire
    PRIMARY KEY (id),  -- Définition de la clé primaire
    FOREIGN KEY (id_commerce) REFERENCES commerce(id) ON DELETE CASCADE,  -- Clé étrangère vers commerce
    FOREIGN KEY (id_produit) REFERENCES produit(id) ON DELETE CASCADE  -- Clé étrangère vers produit
);

-- Création de la table 'echange'
CREATE TABLE IF NOT EXISTS echange (
    id BIGINT AUTO_INCREMENT,  -- Ajout d'AUTO_INCREMENT pour générer automatiquement les IDs
    id_offre BIGINT NOT NULL,  -- Référence à l'offre
    id_association BIGINT NOT NULL,  -- Référence à l'association
    date_echange DATE NOT NULL,  -- Date de l'échange obligatoire
    PRIMARY KEY (id),  -- Définition de la clé primaire
    FOREIGN KEY (id_association) REFERENCES association(id) ON DELETE CASCADE,  -- Clé étrangère vers association
    FOREIGN KEY (id_offre) REFERENCES offre(id) ON DELETE CASCADE  -- Clé étrangère vers offre
);
