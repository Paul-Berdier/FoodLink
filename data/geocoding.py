import requests

def get_coordinates(adresse, ville):
    """
    Récupère les coordonnées géographiques en JSON à partir d'une adresse et d'une ville.

    :param adresse: Adresse de l'utilisateur (rue et numéro)
    :param ville: Ville de l'utilisateur
    :return: Dictionnaire contenant les coordonnées ou un message d'erreur
    """
    query = f"{adresse} {ville}"
    url = f"https://api-adresse.data.gouv.fr/search/?q={query}&type=street"

    try:
        response = requests.get(url, timeout=5)  # Ajout d'un timeout pour éviter des blocages prolongés
        if response.status_code == 200:
            data = response.json()
            if data["features"]:
                return {
                    "success": True,
                    "coordinates": data["features"][0]["geometry"]
                }
            else:
                return {
                    "success": False,
                    "error": "Aucun résultat trouvé pour cette adresse."
                }
        else:
            return {
                "success": False,
                "error": f"Erreur API: {response.status_code}"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Le service de géocodage a mis trop de temps à répondre."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur inattendue : {str(e)}"
        }
