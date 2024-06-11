import os
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium import Popup, GeoJsonPopup
from streamlit_folium import st_folium
import data_helper
import random

# Load data
data = data_helper.load_global_data_and_labels()

# Constants
MAP_EMOJI_URL = "./Logo.png"

# Streamlit page configuration
st.set_page_config(
    page_title="Global Heat Resilience Service", 
    page_icon=MAP_EMOJI_URL,
    layout="wide"
)

# Utility functions
def get_random_color():
    r = random.randrange(0, 256)
    g = random.randrange(0, 256)
    b = random.randrange(0, 256)
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def create_style_function(fill_color, border_color=None):
    def style_function(feature):
        return {
            'fillColor': fill_color,
            'color': border_color,  # Hide the border
            'fillOpacity': 0.75,
            'weight': 0.5
        }
    return style_function

# Header section
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(MAP_EMOJI_URL, width=160)
st.title("Global Heat Resilience Service")
st.markdown('''
Cities worldwide face the critical challenge of understanding and addressing localized extreme heat risks...
''')
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# Main content
col1, col2 = st.columns([3, 2])

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 5
if "markers_2020" not in st.session_state:
    st.session_state["markers_2020"] = []
if "markers_2030" not in st.session_state:
    st.session_state["markers_2030"] = []
if "markers_2050" not in st.session_state:
    st.session_state["markers_2050"] = []

# Create global map
global_map = folium.Map(location=[0, 0], zoom_start=5)
folium.TileLayer(
    tiles='Stamen Toner',  
    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> | Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
).add_to(global_map)

# Add markers to global map
for f in data:
    facility_id = str(f["properties"]["ID_HDC_G0"])
    marker = folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup(facility_id, parse_html=False),
        tooltip="Tooltip!"
    )
    marker.add_to(global_map)

# Display global map
with col1:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    global_map_obj = st_folium(global_map, width=900, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

    # Create city-specific map
    city_map = folium.Map(location=[0, 0], zoom_start=8, min_zoom=3, max_zoom=10)
    fg_2020 = folium.FeatureGroup(name="2020", overlay=True, show=True)

    # Add feature group to city map
    for marker in st.session_state["markers_2020"]:
        fg_2020.add_child(marker)

    # Update city map based on global map interaction
    if global_map_obj["last_object_clicked_popup"] is not None:
        clicked_marker = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
        if clicked_marker is not None:
            location = [clicked_marker['GCPNT_LAT'], clicked_marker['GCPNT_LON']]
            city_map.fit_bounds([location, location], max_zoom=10)

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    city_map_obj = st_folium(
        city_map,
        key="city_map",
        feature_group_to_add=[fg_2020],
        height=400,
        width=900,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Display city information
with col2:
    properties = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])

    if properties is not None:
        st.session_state["markers_2020"] = []
        st.markdown("### City Information")
        st.markdown("<p style='font-size: 14px;'><b>Country Name:</b> {}</p>".format(properties["CTR_MN_NM"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Total Area of Urban Centres in 2000:</b> {} sq km</p>".format(properties["H00_AREA"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>City Name:</b> {}</p>".format(properties["UC_NM_MN"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Total Built-up Area in 2015:</b> {} sq km</p>".format(round(properties["B15"], 0)), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Area:</b> {} sq km</p>".format(properties["AREA"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Average Temperature for Epoch 2014:</b> {} °C</p>".format(round(properties["E_WR_T_14"], 1)), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Total Resident Population in 2015:</b> {}</p>".format(properties["P15"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Sum of GDP PPP Values for Year 2015:</b> {}</p>".format(properties["GDP15_SM"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Average Greenness in 2014:</b> {}</p>".format(properties["E_GR_AV14"]), unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px;'><b>Maximum Magnitude of the Heatwaves:</b> {}</p>".format(properties["EX_HW_IDX"]), unsafe_allow_html=True)

        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data is not None:
            for f in city_data:
                # 2020
                if "colRange_2020" in f["properties"]:
                    if f["properties"]["colRange_2020"] is not None:
                        fillColorProperties = f["properties"]["colRange_2020"]
                        color = "#000000"
                    else:
                        fillColorProperties = None
                        color = 'rgba(0, 0, 0, 0)'
                else:
                    color = get_random_color()
                style_function = create_style_function(fill_color=fillColorProperties, border_color=color)
                marker = folium.GeoJson(
                    f,
                    popup=folium.features.GeoJsonPopup(fields=["Name", "_median", "_median_2", "_median_3"],
                                                       aliases=[
                                                           'Name',
                                                           'Year 2020',
                                                           'Year 2030',
                                                           'Year 2050'],
                                                       labels=True),
                    style_function=style_function
                )
                marker.add_to(city_map)
                st.session_state["markers_2020"].append(marker)

        properties = city_map_obj["last_object_clicked_popup"]
        st.write(properties)

# Download button
with open(os.path.join("data", "Rome Urban Heat Resilience Profile.pdf"), "rb") as file:
    btn = st.download_button(label="Download data", data=file, file_name="Rome Urban Heat Resilience Profile.pdf", mime="application/pdf")

st.divider()

# Data browser section
with st.expander("Browse available data"):
    components.iframe('https://geo-dev-hub.maps.arcgis.com/apps/mapviewer/index.html?webmap=4c17c5dd3cba457e80e6c546bc73a3b1', height=500)

st.divider()

# Methodology section
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.header("Methodology")
st.markdown('''
The heat map visually represents the distribution of extreme heat within the city, highlighting areas with varying temperature intensities...
''')
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# Historical data section
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.header("Historical Data")
st.markdown('''
The Historical Temperature Data section provides an in-depth analysis of past temperature trends within the city...
''')
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# Footer
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown('''
© 2024 Global Heat Resilience Service. All Rights Reserved. For more information, please contact us at:
Email: heatresilience@geosec.org 
Phone: +41 22 730 8251
Visit our main website: Earth Observations
''')

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('''
    ### Useful Links:
    - Privacy Policy
    - Terms of Service
    - Help & Support
    - About Us
    - Data Sources
    - Partners
    ''')

with col2:
    st.markdown('''
    ### Follow Us:
    - Facebook
    - Twitter
    - LinkedIn 
    ''')

st.markdown("Global Heat Resilience Service is part of the Group on Earth Observations (GEO) community, dedicated to fostering global collaboration for a sustainable planet.")
st.markdown("</div>", unsafe_allow_html=True)
