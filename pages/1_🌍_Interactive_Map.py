import streamlit as st
import osmnx as ox
import leafmap.foliumap as leafmap
import geopandas as gpd
import io

# Titre de l'application Streamlit
st.title("Réseaux Électriques OSM")

# Sélectionner la zone géographique (ici, tu peux spécifier un lieu, une ville, ou une zone particulière)
place_name = st.text_input("Nom de la ville ou de la zone (ex. Paris, France)", "Paris, France")

# Télécharger les données OSM pour les lignes électriques et les sous-stations
@st.cache
def download_osm_data(place_name):
    # Récupérer les lignes électriques (réseau électrique haute tension, etc.)
    tags = {"power": "line"}
    power_lines = ox.geometries_from_place(place_name, tags=tags)

    # Récupérer les sous-stations
    tags_substation = {"power": "substation"}
    substations = ox.geometries_from_place(place_name, tags=tags_substation)

    return power_lines, substations

# Charger les données OSM (lignes électriques et sous-stations)
power_lines, substations = download_osm_data(place_name)

# Affichage des résultats
st.write(f"### Lignes électriques et sous-stations dans {place_name}")

# Créer une carte interactive avec `leafmap`
m = leafmap.Map(center=[48.8566, 2.3522], zoom=12)

# Ajouter les lignes électriques à la carte (si des données sont disponibles)
if not power_lines.empty:
    m.add_gdf(power_lines, layer_name="Lignes électriques", color="blue", opacity=0.7)

# Ajouter les sous-stations à la carte (si des données sont disponibles)
if not substations.empty:
    m.add_gdf(substations, layer_name="Sous-stations", color="red", opacity=0.7)

# Afficher la carte sur Streamlit
m.to_streamlit(height=700)

# Télécharger les données sous forme de GeoJSON, GeoPackage, GeoParquet ou KML
@st.cache
def convert_to_geojson(gdf):
    return gdf.to_json()

@st.cache
def convert_to_geopackage(gdf, place_name):
    buffer = io.BytesIO()
    gdf.to_file(buffer, driver="GPKG", layer=place_name)
    buffer.seek(0)
    return buffer.read()

@st.cache
def convert_to_geoparquet(gdf, place_name):
    buffer = io.BytesIO()
    gdf.to_parquet(buffer)
    buffer.seek(0)
    return buffer.read()

@st.cache
def convert_to_kml(gdf, place_name):
    buffer = io.BytesIO()
    gdf.to_file(buffer, driver="KML")
    buffer.seek(0)
    return buffer.read()

# Créer un bouton pour télécharger les données OSM en GeoJSON, GeoPackage, GeoParquet ou KML
st.subheader("Télécharger les données")

# Fusionner les données des lignes et sous-stations dans un seul GeoDataFrame
if not power_lines.empty or not substations.empty:
    all_data = power_lines.append(substations)
    
    # Choisir le format de téléchargement
    download_format = st.radio("Choisir le format de téléchargement", ("GeoJSON", "GeoPackage", "GeoParquet", "KML"))
    
    if download_format == "GeoJSON":
        geojson_data = convert_to_geojson(all_data)
        st.download_button(
            label="Télécharger en GeoJSON",
            data=geojson_data,
            file_name=f"reseau_electrique_{place_name.replace(' ', '_')}.geojson",
            mime="application/geo+json"
        )
    elif download_format == "GeoPackage":
        geopackage_data = convert_to_geopackage(all_data, place_name)
        st.download_button(
            label="Télécharger en GeoPackage",
            data=geopackage_data,
            file_name=f"reseau_electrique_{place_name.replace(' ', '_')}.gpkg",
            mime="application/geopackage+sqlite3"
        )
    elif download_format == "GeoParquet":
        geoparquet_data = convert_to_geoparquet(all_data, place_name)
        st.download_button(
            label="Télécharger en GeoParquet",
            data=geoparquet_data,
            file_name=f"reseau_electrique_{place_name.replace(' ', '_')}.parquet",
            mime="application/octet-stream"
        )
    elif download_format == "KML":
        kml_data = convert_to_kml(all_data, place_name)
        st.download_button(
            label="Télécharger en KML",
            data=kml_data,
            file_name=f"reseau_electrique_{place_name.replace(' ', '_')}.kml",
            mime="application/vnd.google-earth.kml+xml"
        )
