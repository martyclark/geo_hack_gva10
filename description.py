import streamlit as st
import streamlit.components.v1 as components
import folium
from folium import Popup
from streamlit_folium import st_folium
import data_helper
import random

data = data_helper.load_global_data_and_labels()

MAP_EMOJI_URL = "./logo.png"

st.set_page_config(
    page_title="Global Heat Resilience Service", 
    page_icon=MAP_EMOJI_URL,
    layout="wide")


def get_random_color():
    r = random.randrange(0, 256)
    g = random.randrange(0, 256)
    b = random.randrange(0, 256)
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)


def create_style_function(fill_color, border_color=None):
    def style_function(feature):
        return {
            'fillColor': fill_color,
            'color': border_color,  # Hide the border
            'fillOpacity': 0.75,
            'weight': 0.5
        }
    return style_function


col6, col7,col8 = st.columns([1,5,1])
col6.write("")
with col7:
    st.image(MAP_EMOJI_URL, width=160)
    st.title("Global Heat Resilience Service")
    st.write('''Cities worldwide face the critical challenge of understanding and addressing localized extreme heat risks, a top climate change concern. The Global Heat Resilience Service is designed to empower urban decision-makers with the comprehensive data needed to prioritize and tackle this issue effectively. Our platform seamlessly integrates existing open global data, providing detailed neighborhood-level insights into heat vulnerability. It captures key factors such as demographics, socio-economic status, and access to essential services, which traditional methods often overlook.   
          
With our user-friendly interface, information that was once inaccessible and fragmented is now consolidated and easily navigable. The Global Heat Resilience Service offers a robust combination of hazard, exposure, and vulnerability data, enabling users to assess heat vulnerability under both current and future climatic conditions. Our clear maps and data visualizations highlight the location and number of people exposed and vulnerable, detailing impacts on health, economic losses, and more. By presenting these insights in an accessible format, the Global Heat Resilience Service supports cities in making informed decisions and implementing effective strategies to protect their communities from the growing threat of extreme heat. Join us in building more resilient urban environments and safeguarding the well-being of residents worldwide.''')
col8.write("")
st.divider()


col1, col2 = st.columns([2, 1])

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 5
if "markers" not in st.session_state:
    st.session_state["markers"] = []

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
    city_map = folium.Map(location=[0, 0], zoom_start=8, min_zoom=3, max_zoom=10)
    fg = folium.FeatureGroup(name="Markers")
    for marker in st.session_state["markers"]:
        fg.add_child(marker)

 # Update zoom level and center location when a marker is clicked
    if global_map_obj["last_object_clicked_popup"] is not None:
        st.session_state["zoom"] = 8  # or any other zoom level you prefer
        # Get the coordinates of the clicked marker
        clicked_marker = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
        if clicked_marker is not None:
            # Combine latitude and longitude into a list
            location = [clicked_marker['GCPNT_LAT'], clicked_marker['GCPNT_LON']]
            # city_map = folium.Map(location=location, zoom_start=st.session_state["zoom"], min_zoom=3, max_zoom=10)
            city_map.fit_bounds([location, location], max_zoom=10)

    st_folium(
        city_map,
        key="city_map",
        feature_group_to_add=fg,
        height=400,
        width=900,
    )

with (col2):
    col3, col4, col5 = st.columns(3)
    properties = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
    if properties is not None:
        st.session_state["markers"] = []
        with col3:
            st.metric("Country name", properties["CTR_MN_NM"])
            st.write("Total area of Urban Centres in 2000:")
            st.subheader(properties["H00_AREA"])
        with col4:
            st.metric("City name", properties["UC_NM_MN"])
            st.write("Total built-up area in 2015:")
            st.subheader(round(properties["B15"],0))
        with col5:
            st.metric ("Area", properties["AREA"]) 
            st.write("Average temperature for epoch 2014:")
            st.subheader(round(properties["E_WR_T_14"], 1))
        st.write("Total resident population in 2015:", properties["P15"])
        st.write("Sum of GDP PPP values for year 2015:", properties["GDP15_SM"])
        st.write("Average greenness estimated for 2014 located in the built-up area of epoch 2014:", properties["E_GR_AV14"])
        st.write("Maximum magnitude of the heatwaves", properties["EX_HW_IDX"])

        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data is not None:
            for f in city_data:
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
                    style_function=style_function
                )
                st.session_state["markers"].append(marker.add_to(city_map))

st.divider()


with st.expander("Further information about the data"):
    components.iframe('https://geo-dev-hub.maps.arcgis.com/apps/mapviewer/index.html?webmap=4c17c5dd3cba457e80e6c546bc73a3b1', height=500)
    
st.divider()

col11, col12, col13 = st.columns([1,5,1])

with col12:
    st.header("Methodology")
    st.write(''' The heat map visually represents the distribution of extreme heat within the city, highlighting areas with varying temperature intensities. Warmer colors, such as red and orange, indicate higher temperatures and greater heat risk, while cooler colors, such as blue and green, represent lower temperatures and lesser risk.''')
    st.markdown(''' ## How to Interpret the Heat Map
                
### High-Risk Areas  
                
Look for regions shaded in red or dark orange, which signify zones with the highest temperatures and potential heat-related impacts.  
### Moderate-Risk Areas  
                
Yellow and light orange areas indicate moderate temperatures and a need for some heat mitigation measures.  
                
### Low-Risk Areas  
                
Green and blue regions denote cooler areas with lower heat risk.''')
    st.divider()

    st.header("Historical data")
    st.write('''The Historical Temperature Data section provides an in-depth analysis of past temperature trends within the city. This section includes comprehensive data on daily, monthly, and annual temperature variations over the past several decades. By examining historical temperature records, users can identify long-term trends, such as increasing average temperatures, the frequency and intensity of heatwaves, and seasonal patterns.''')  
    st.subheader("Key Features")
    st.write('''Temperature Trends: Visual graphs and charts showing how temperatures have changed over time.
Heatwave Analysis: Data on the occurrence, duration, and severity of past heatwaves.
Seasonal Patterns: Insights into temperature fluctuations across different seasons, highlighting periods of extreme heat.
Comparison with Averages: Comparisons of historical temperatures with long-term climate averages to identify anomalies and significant changes.''')

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
