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
Cities worldwide face the critical challenge of understanding and addressing localized extreme heat risks, a top climate change concern. The Global Heat Resilience Service is designed to empower urban decision-makers with the comprehensive data needed to prioritize and tackle this issue effectively. Our platform seamlessly integrates existing open global data, providing detailed neighborhood-level insights into heat vulnerability. It captures key factors such as demographics, socio-economic status, and access to essential services, which traditional methods often overlook.   
          
With our user-friendly interface, information that was once inaccessible and fragmented is now consolidated and easily navigable. The Global Heat Resilience Service offers a robust combination of hazard, exposure, and vulnerability data, enabling users to assess heat vulnerability under both current and future climatic conditions. Our clear maps and data visualizations highlight the location and number of people exposed and vulnerable, detailing impacts on health, economic losses, and more. By presenting these insights in an accessible format, the Global Heat Resilience Service supports cities in making informed decisions and implementing effective strategies to protect their communities from the growing threat of extreme heat. 

Join us in building more resilient urban environments and safeguarding the well-being of residents worldwide.
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
    properties = data_helper.get_data_by_id(data, global_map_obj.get("last_object_clicked_popup"))
    if properties:
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        st.markdown(f"### Country name: {properties['CTR_MN_NM']}")
        st.markdown(f"### City name: {properties['UC_NM_MN']}")
        st.markdown(f"### Area: {properties['AREA']}")
        st.markdown(f"**Total area of Urban Centres in 2000:** {properties['H00_AREA']}")
        st.markdown(f"**Total built-up area in 2015:** {round(properties['B15'], 0)}")
        st.markdown(f"**Average temperature for epoch 2014:** {round(properties['E_WR_T_14'], 1)}")
        st.markdown(f"**Total resident population in 2015:** {properties['P15']}")
        st.markdown(f"**Sum of GDP PPP values for year 2015:** {properties['GDP15_SM']}")
        st.markdown(f"**Average greenness estimated for 2014 located in the built-up area of epoch 2014:** {properties['E_GR_AV14']}")
        st.markdown(f"**Maximum magnitude of the heatwaves:** {properties['EX_HW_IDX']}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### City Data for Kpone Katamanso")
        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data:
            for f in city_data:
                st.markdown(f"**Name:** {f['properties']['Name']}")
                st.markdown(f"**Year 2020:** {f['properties']['colRange_2020']}")
                st.markdown(f"**Year 2030:** {f['properties']['colRange_2030']}")
                st.markdown(f"**Year 2050:** {f['properties']['colRange_2050']}")
                marker = folium.GeoJson(
                    f,
                    popup=folium.features.GeoJsonPopup(fields=["Name", "_median", "_median_2", "_median_3"],
                                                       aliases=['Name', 'Year 2020', 'Year 2030', 'Year 2050'],
                                                       labels=True),
                    style_function=create_style_function(fill_color=f['properties'].get('colRange_2020', '#FFFFFF'))
                )
                marker.add_to(city_map)
                st.session_state.setdefault("markers_2020", []).append(marker)
                
with open(os.path.join("data", "Rome Urban Heat Resilience Profile.pdf"), "rb") as file:
    btn = st.download_button(label ="Download data", data = file, file_name = "Rome Urban Heat Resilience Profile.pdf", mime = "application/pdf")

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
