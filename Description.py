from streamlit_folium import st_folium
from folium import Popup
import folium
import streamlit as st

import data_helper

data = data_helper.load_data_and_labels()

# Set page layout to wide
st.set_page_config(layout="wide")

st.write("# Welcome to our Project! 👋")

# Create two columns with the first one being twice as wide as the second
col1, col2 = st.columns([2,1])

# Add a map to the first column
col1.map()

# Add text to the second column
col2.markdown(
    """
    Placeholder text for overall info / info about specific country
    """
)

# center on Liberty Bell, add marker
m = folium.Map(location=[0, 0], zoom_start=5)

for f in data:
    folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup("Popup!", parse_html=False),
        tooltip="Tooltip!",
    ).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)

m = folium.Map(location=[45, -122], zoom_start=4)

folium.Marker(
    location=[45.5, -122],
    popup=Popup("Popup!", parse_html=False),
    tooltip="Tooltip!",
).add_to(m)

folium.Marker(
    location=[45.5, -112],
    popup=Popup("Popup 2!", parse_html=False),
    tooltip="Tooltip 2!",
).add_to(m)

out = st_folium(m, height=200)

st.write("Popup:", out["last_object_clicked_popup"])
st.write("Tooltip:", out["last_object_clicked_tooltip"])