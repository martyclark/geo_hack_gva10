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

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 5
if "markers" not in st.session_state:
    st.session_state["markers"] = []

global_map = folium.Map(location=[0, 0], zoom_start=5)
btn_expand = st.button("display in second map")

for f in data:
    facility_id = str(f["properties"]["ID_HDC_G0"])
    marker = folium.Marker(
        location=f['geometry']['coordinates'][::-1],
        popup=Popup(facility_id, parse_html=False),
        tooltip="Tooltip!"
    )
    marker.add_to(global_map)

# Add a button to the right column
with col1:
    # Render Folium map in Streamlit
    global_map_obj = st_folium(global_map, width=900, height=400)
    city_map = folium.Map(location=[0, 0], zoom_start=8)
    fg = folium.FeatureGroup(name="Markers")
    for marker in st.session_state["markers"]:
        fg.add_child(marker)

    st_folium(
        city_map,
        zoom=st.session_state["zoom"],
        key="new",
        feature_group_to_add=fg,
        height=400,
        width=700,
    )

# Display the popup and tooltip information
with col2:
    col3, col4,col5 = st.columns(3)
    properties = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
    if properties is not None:
        with col3:
            st.subheader("Country name:")
            st.subheader(properties["CTR_MN_NM"])
            st.divider()
            st.write("Total area of Urban Centres in 2000:")
            st.subheader(properties["H00_AREA"])
            st.write("Average temperature for epoch 2014:")
            st.subheader(round(properties["E_WR_T_14"], 1))
        with col4:
            st.subheader("City name:")
            st.subheader(properties["UC_NM_MN"])
            st.divider()
            st.write("Total built-up area in 2015:")
            st.subheader(round(properties["B15"],0))
            st.write("Total resident population in 2015:", properties["P15"])
            st.write("Sum of GDP PPP values for year 2015:", properties["GDP15_SM"])
        with col5: 
            st.subheader("Area:")
            st.metric ("", properties["AREA"]) 
            st.divider()
            st.write("Average greenness estimated for 2014 located in the built-up area of epoch 2014:", properties["E_GR_AV14"])
            st.write("Maximum magnitude of the heatwaves", properties["EX_HW_IDX"])
        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())
        if city_data is not None:

            for f in city_data:
                folium.GeoJson(f).add_to(city_map)
                marker = folium.GeoJson(f)
                # print(marker.data["geometry"]["coordinates"])
            #     lat, lon = marker.location
                st.session_state["markers"].append(marker.add_to(city_map))
            #     if lat < most_southwest[0] or (lat == most_southwest[0] and lon < most_southwest[1]):
            #         most_southwest = marker.location
            #
            #     # Update the most northeast marker
            #     if lat > most_northeast[0] or (lat == most_northeast[0] and lon > most_northeast[1]):
            #         most_northeast = marker.location
            # city_map.fit_bounds([most_southwest, most_northeast])

if btn_expand:
    random_marker = folium.Marker(
        location=[5.621085071, -0.215586875],
        popup=f"Random marker at [5.621085071, -0.215586875]",
    )
    st.session_state["markers"].append(random_marker)
