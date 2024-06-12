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

# First container: Global map and city information
with st.container():
    col1, col2 = st.columns([3, 2])

    with col1:
        global_map = folium.Map(location=[0, 0], zoom_start=5)
        folium.TileLayer(
            tiles='Stamen Toner',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> | Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        ).add_to(global_map)

        for f in data:
            facility_id = str(f["properties"]["ID_HDC_G0"])
            marker = folium.Marker(
                location=f['geometry']['coordinates'][::-1],
                popup=Popup(facility_id, parse_html=False),
                tooltip="Tooltip!"
            )
            marker.add_to(global_map)

        global_map_obj = st_folium(global_map, width=800, height=400)

    with col2:
        properties = data_helper.get_data_by_id(data, global_map_obj.get("last_object_clicked_popup"))
        if properties:
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Country name", properties["CTR_MN_NM"])
                st.write("Total area of Urban Centres in 2000:")
                st.subheader(properties["H00_AREA"])
            with col4:
                st.metric("City name", properties["UC_NM_MN"])
                st.write("Total built-up area in 2015:")
                st.subheader(round(properties["B15"], 0))
            with col5:
                st.metric("Area", properties["AREA"])
                st.write("Average temperature for epoch 2014:")
                st.subheader(round(properties["E_WR_T_14"], 1))
            st.write("Total resident population in 2015:", properties["P15"])
            st.write("Sum of GDP PPP values for year 2015:", properties["GDP15_SM"])
            st.write("Average greenness estimated for 2014 located in the built-up area of epoch 2014:", properties["E_GR_AV14"])
            st.write("Maximum magnitude of the heatwaves:", properties["EX_HW_IDX"])

st.divider()

# Second container: City map and city data
with st.container():
    col6, col7 = st.columns([3, 2])

    with col6:
        city_map = folium.Map(location=[0, 0], zoom_start=8, min_zoom=3, max_zoom=10)
        fg_2020 = folium.FeatureGroup(name="2020", overlay=True, show=True)
        city_map.add_child(fg_2020)

        if global_map_obj.get("last_object_clicked_popup"):
            clicked_marker = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
            if clicked_marker:
                location = [clicked_marker['GCPNT_LAT'], clicked_marker['GCPNT_LON']]
                city_map.fit_bounds([location, location], max_zoom=10)

        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data:
            st.session_state["markers_2020"] = []
            for f in city_data:
                if "colRange_2020" in f["properties"]:
                    fillColorProperties = f["properties"]["colRange_2020"] or 'rgba(0, 0, 0, 0)'
                else:
                    fillColorProperties = get_random_color()
                style_function = create_style_function(fill_color=fillColorProperties, border_color="#000000")
                marker = folium.GeoJson(
                    f,
                    popup=folium.features.GeoJsonPopup(fields=["Name", "_median", "_median_2", "_median_3"],
                                                       aliases=['Name', 'Year 2020', 'Year 2030', 'Year 2050'],
                                                       labels=True),
                    style_function=style_function
                )
                marker.add_to(city_map)
                st.session_state["markers_2020"].append(marker)

        city_map_obj = st_folium(city_map, key="city_map", width=800, height=400)

    with col7:
        if "last_object_clicked_popup" in st.session_state:
            properties = st.session_state["last_object_clicked_popup"]
            if properties:
                st.subheader("District-level heat risk assessment")
                
                # Check if the properties structure is as expected
                if isinstance(properties, dict):
                    # Convert properties to a DataFrame and display it as a table
                    df = pd.DataFrame(list(properties.items()), columns=["Property", "Value"])
                    st.table(df)
                else:
                    st.write("No properties to display or unexpected data structure.")
        
# Download button
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
The heat map visually represents the distribution of extreme heat within the city, highlighting areas with varying temperature intensities. Warmer colors, such as red and orange, indicate higher temperatures and greater heat risk, while cooler colors, such as blue and green, represent lower temperatures and lesser risk.
    A heat risk index is a composite measure that quantifies the potential harm of high temperatures to a given population or area. It is created by integrating three key components: 
    
    Hazard: This represents the intensity and duration of heat events, often measured using metrics like maximum daily temperature, heatwave duration, or the number of days exceeding a certain temperature threshold. Exposure: This accounts for the degree to which individuals or communities are exposed to the heat hazard, considering factors such as population density, land cover, and the presence of heat-mitigating infrastructure like green spaces or cooling centers. 
    
    Vulnerability: This captures the susceptibility of individuals or communities to the adverse effects of heat, taking into account factors like age, health conditions, socioeconomic status, and access to resources. 
    
    By combining data on these three components, a heat risk index provides a comprehensive assessment of the overall risk posed by high temperatures. This index can then be used to identify vulnerable populations and areas, inform targeted interventions and adaptation strategies, and monitor the effectiveness of heat mitigation efforts over time.
''')
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.header("Historical Data")
st.markdown('''
## How to Interpret the Heat Map
                
### High-Risk Areas  
                
Look for regions shaded in red or dark orange, which signify zones with the highest temperatures and potential heat-related impacts.  
### Moderate-Risk Areas  
                
Yellow and light orange areas indicate moderate temperatures and a need for some heat mitigation measures.  
                
### Low-Risk Areas  
                
Green and blue regions denote cooler areas with lower heat risk.
''')
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

st.header("Historical data")
st.write('''The Historical Temperature Data section provides an in-depth analysis of past temperature trends within the city. This section includes comprehensive data on daily, monthly, and annual temperature variations over the past several decades. By examining historical temperature records, users can identify long-term trends, such as increasing average temperatures, the frequency and intensity of heatwaves, and seasonal patterns.''')  
st.subheader("Key Features")
st.write('''Temperature Trends: Visual graphs and charts showing how temperatures have changed over time. Heatwave Analysis: Data on the occurrence, duration, and severity of past heatwaves. Seasonal Patterns: Insights into temperature fluctuations across different seasons, highlighting periods of extreme heat. Comparison with Averages: Comparisons of historical temperatures with long-term climate averages to identify anomalies and significant changes.''')

st.subheader("How to Use This Section")

st.write('''Users can leverage the historical temperature data to:

Understand Long-Term Changes: Gain insights into how the city's climate has evolved, helping to predict future trends.
Inform Planning and Policy: Use historical data to support urban planning decisions and the development of heat mitigation strategies.
Raise Awareness: Educate the community and stakeholders about historical temperature patterns and their implications for future heat resilience.''')

st.divider()

st.markdown(''' © 2024 Global Heat Resilience Service. All Rights Reserved. For more information, please contact us at:

Email: heatresilience@geosec.org 
Phone: +41 22 730 8251

Visit our main website: Earth Observations''')

col9, col10 = st.columns([1,1])

with col9:
    st.write('''
Useful Links:

    Privacy Policy
    Terms of Service
    Help & Support
    About Us
    Data Sources
    Partners
''')
    
with col10:
    st.write('''
Follow Us:

    Facebook
    Twitter
    LinkedIn 
''')

st.markdown("Global Heat Resilience Service is part of the Group on Earth Observations (GEO) community, dedicated to fostering global collaboration for a sustainable planet.")
