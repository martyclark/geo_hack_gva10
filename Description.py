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

# center on Liberty Bell, add marker
m = folium.Map(location=[0, 0], zoom_start=5)

for f in data:
    folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup("Popup!", parse_html=False),
        tooltip="Tooltip!",
    ).add_to(m)

# call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)

with col1:
    out = st_folium(m, width=700)
with col2:
    st.write("Popup:", out["last_object_clicked_popup"])
    st.write("Tooltip:", out["last_object_clicked_tooltip"])


