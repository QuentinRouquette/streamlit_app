import streamlit as st
import osmnx as ox
import leafmap.foliumap as leafmap
import geopandas as gpd

# Titre de l'application Streamlit
st.title("Réseaux Électriques OSM - Test")

# Sélectionner la zone géographique (ici, tu peux spécifier un lieu, une ville, ou une zone particulière)
place_name = st.text_input("Nom de la ville ou de la zone (ex. Paris, France)", "Paris, France")

# Télécharger les données OSM pour les lignes électriques et les sous-stations
@st.cache
def download_osm_data(place_name):
    # Utilisation d'OSMnx pour récupérer les lignes électriques et les sous-stations
    try:
        # Récupérer les lignes électriques
        tags = {"power": "line"}
        power_lines = ox.geometries_from_place(place_name, tags=tags)

        # Récupérer les sous-stations
        tags_substation = {"power": "substation"}
        substations = ox.geometries_from_place(place_name, tags=tags_substation)

        return power_lines, substations
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données OSM : {str(e)}")
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()  # Retourner des GeoDataFrames vides en cas d'erreur

# Charger les données OSM (lignes électriques et sous-stations)
if place_name:
    power_lines, substations = download_osm_data(place_name)

    # Affichage des résultats
    st.write(f"### Lignes électriques et sous-stations dans {place_name}")

    # Créer une carte interactive avec `leafmap`
    m = leafmap.Map(center=[48.8566, 2.3522], zoom=12)  # Par défaut, Paris, mais tu peux ajuster avec `place_name`

    # Ajouter les lignes électriques à la carte (si des données sont disponibles)
    if not power_lines.empty:
        m.add_gdf(power_lines, layer_name="Lignes électriques", color="blue", opacity=0.7)

    # Ajouter les sous-stations à la carte (si des données sont disponibles)
    if not substations.empty:
        m.add_gdf(substations, layer_name="Sous-stations", color="red", opacity=0.7)

    # Afficher la carte sur Streamlit
    m.to_streamlit(height=700)

else:
    st.write("Entrez un nom de lieu pour commencer à charger les données.")
