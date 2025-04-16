import requests
import folium

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


def generate_route_map(start, end):
    """
    Génère une carte avec les itinéraires pour les modes de transport 'driving', 'cycling' et 'foot'.

    :param start: Tuple (latitude, longitude) des coordonnées de départ
    :param end: Tuple (latitude, longitude) des coordonnées d'arrivée
    :return: HTML sous forme de chaîne de caractères
    """
    osrm_url = "http://router.project-osrm.org/route/v1"
    profiles = ["driving", "cycling", "foot"]
    colors = {"driving": "blue", "cycling": "green", "foot": "red"}

    mymap = folium.Map(location=start, zoom_start=6)

    for profile in profiles:
        coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
        response = requests.get(f"{osrm_url}/{profile}/{coordinates}?geometries=geojson&overview=full")

        if response.status_code == 200:
            data = response.json()
            route = data['routes'][0]

            distance_km = route['distance'] / 1000
            duration_minutes = route['duration'] / 60

            print(
                f"Mode: {profile.capitalize()} - Distance : {distance_km:.2f} km, Durée : {duration_minutes:.2f} minutes")

            folium.PolyLine(
                locations=[(coord[1], coord[0]) for coord in route['geometry']['coordinates']],
                color=colors[profile],
                weight=5,
                opacity=0.7,
                tooltip=f"{profile.capitalize()} - {distance_km:.2f} km"
            ).add_to(mymap)
        else:
            print(f"Erreur pour le mode {profile}: {response.status_code}, {response.text}")

    return mymap._repr_html_()


# Exemple d'utilisation
html_map = generate_route_map((47.218371, -1.563546), (48.8534, 2.3488))