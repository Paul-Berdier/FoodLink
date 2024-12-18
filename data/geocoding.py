import requests

def get_coordinates(adresse, ville):
    """
    Récupère les coordonnées géographiques en JSON à partir d'une adresse et d'une ville.

    :param adresse: Adresse de l'utilisateur (rue et numéro)
    :param ville: Ville de l'utilisateur
    :return: Dictionnaire JSON contenant les coordonnées ou un message d'erreur
    """
    query = f"{adresse} {ville}"
    url = f"https://api-adresse.data.gouv.fr/search/?q={query}&type=street"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["features"]:
                return data["features"][0]["geometry"]  # Retourne les coordonnées JSON
            else:
                return {"error": "Aucun résultat trouvé"}
        else:
            return {"error": f"Erreur API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
