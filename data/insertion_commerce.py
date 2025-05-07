import pandas as pd
import mysql.connector

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",         # Remplacez par votre hôte
    user="root",              # Remplacez par votre utilisateur MySQL
    password="aAbBcC1928CcBbAa", # Mot de passe
    database="foodlink_bdd"   # Nom de la base de données
)

# Charger le fichier CSV
csv_file = "C:/Users/wajih/OneDrive/Documents/FoodLink/FoodLink/data/commerce.csv"
df = pd.read_csv(csv_file, sep=";")
df['adresse_mail'] = df['adresse_mail'].astype('object')
df['tel'] = df['tel'].astype('object')

print("Types des colonnes dans le CSV :")
print(df.dtypes)

# Remplacer les NaN par None pour les rendre compatibles avec MySQL (NULL)
df = df.where(pd.notnull(df), None)

# Connexion à la base de données
cursor = conn.cursor()

# Préparation de l'insertion
table_name = "commerce"
columns = ",".join(df.columns)  # Obtenir les colonnes du CSV
placeholders = ",".join(["%s"] * len(df.columns))  # Préparer les placeholders (%s)

# Créer la requête d'insertion dynamique
insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

# Insérer les données ligne par ligne depuis le CSV
for _, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))  # Insérer la ligne sous forme de tuple

# Valider et fermer la connexion
conn.commit()
cursor.close()
conn.close()

print("Données insérées avec succès dans la table MySQL.")
