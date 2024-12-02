import streamlit as st
import leafmap.foliumap as leafmap
import requests
from io import BytesIO

# Set the release version and themes
release = "2024-09-18"
themes = ["buildings"]

# Create a function to load PMTiles (you can extend it for other themes)
def load_pmtiles_data(release, themes):
    layers = {}
    for theme in themes:
        url = f"https://overturemaps-tiles-us-west-2-beta.s3.amazonaws.com/{release}/{theme}.pmtiles"
        
        try:
            # Request the PMTiles file
            response = requests.get(url)
            pmtiles_data = BytesIO(response.content)
            layers[theme] = pmtiles_data
            print(f"Loaded {theme} PMTiles data.")
        except Exception as e:
            print(f"Failed to load {theme} data: {e}")
    
    return layers

# Load the PMTiles data
layers = load_pmtiles_data(release, themes)

# Streamlit layout and sidebar
markdown = """
A Streamlit map template
<https://github.com/opengeos/streamlit-map-template>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

st.title("Interactive Map")

# Sidebar controls for basemap selection
col1, col2 = st.columns([4, 1])
options = list(leafmap.basemaps.keys())
index = options.index("OpenTopoMap")

with col2:
    basemap = st.selectbox("Select a basemap:", options, index)

# Create the map
with col1:
    m = leafmap.Map(
        locate_control=True, latlon_control=True, draw_export=True, minimap_control=True
    )
    m.add_basemap(basemap)

    # Add the layers (PMTiles) to the map
    for theme, pmtiles_data in layers.items():
        # Add each PMTiles as a layer to the map (assuming the library supports adding PMTiles directly)
        m.add_pmtiles(pmtiles_data, name=theme)
        print(f"Added {theme} data to the map.")
    
    m.to_streamlit(height=700)

