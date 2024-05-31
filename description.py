import streamlit as st
import folium
from folium import Popup
from streamlit_folium import st_folium
import data_helper

data = data_helper.load_data_and_labels()

# Set page layout to wide
st.set_page_config(layout="wide")

st.write("# Welcome to our Project! 👋")

# Create two columns with the first one being twice as wide as the second
col1, col2 = st.columns([2, 1])

# Center on Liberty Bell and add markers
m = folium.Map(location=[0, 0], zoom_start=5)

for f in data:
    facility_id = str(f["properties"]["ID_HDC_G0"])
    marker = folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup(facility_id, parse_html=False),
        tooltip="Tooltip!"
    )
    marker.add_to(m)

# Add a button to the right column
with col1:
    # Render Folium map in Streamlit
    out = st_folium(m, width=900, height=400)


# Display the popup and tooltip information
with col2:
    properties = data_helper.get_data_by_id(data, out["last_object_clicked_popup"])
    if properties is not None:
        st.write("Info object:", properties)

if out["last_object_clicked_popup"]:
    st.button("Show More Data")
