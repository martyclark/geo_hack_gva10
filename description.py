import streamlit as st
import folium
from folium import Popup
from streamlit_folium import st_folium
import data_helper

data = data_helper.load_global_data_and_labels()

# Set page layout to wide
st.set_page_config(layout="wide")

st.write("# Welcome to our Project! 👋")

# Create two columns with the first one being twice as wide as the second
col1, col2 = st.columns([2, 1])

if "markers" not in st.session_state:
    st.session_state["markers"] = []

city_map = folium.Map(location=[0, 0], zoom_start=5)
global_map = folium.Map(location=[0, 0], zoom_start=5)

for f in data:
    facility_id = str(f["properties"]["ID_HDC_G0"])
    marker = folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup(facility_id, parse_html=False),
        tooltip="Tooltip!"
    )
    marker.add_to(global_map)

with col1:
    global_map_obj = st_folium(global_map, width=900, height=400)
    fg = folium.FeatureGroup(name="Markers")
    for marker in st.session_state["markers"]:
        fg.add_child(marker)
    st_folium(
        city_map,
        key="city_map",
        feature_group_to_add=fg,
        height=400,
        width=900,
    )

with col2:
    properties = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
    if properties is not None:
        st.session_state["markers"] = []
        st.write("Info object:", properties)
        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data is not None:
            for f in city_data:
                marker = folium.GeoJson(f)
                marker.add_to(city_map)
                st.session_state["markers"].append(marker)
