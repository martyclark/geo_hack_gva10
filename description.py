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

if "center" not in st.session_state:
    st.session_state["center"] = [39.949610, -75.150282]
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 8
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


# Display the popup and tooltip information
with col2:
    properties = data_helper.get_data_by_id(data, global_map_obj["last_object_clicked_popup"])
    if properties is not None:
        st.write("Info object:", properties)
        city_data = data_helper.get_heat_map_by_city_name(properties["UC_NM_MN"].lower())

    with st.echo(code_location="below"):
        city_map = folium.Map(location=[0, 0], zoom_start=5)
        fg = folium.FeatureGroup(name="Markers")
        for marker in st.session_state["markers"]:
            fg.add_child(marker)

        st_folium(
            city_map,
            center=st.session_state["center"],
            zoom=st.session_state["zoom"],
            key="new",
            feature_group_to_add=fg,
            height=400,
            width=700,
        )


# city_map = folium.Map(location=[0, 0], zoom_start=5)
if btn_expand:
    random_marker = folium.Marker(
        location=[5.621085071, -0.215586875],
        popup=f"Random marker at [5.621085071, -0.215586875]",
    )
    st.session_state["markers"].append(random_marker)


# with st.form(key="form_display_city_map"):
#     fg = folium.FeatureGroup(name="Markers")
#     for marker in st.session_state["markers"]:
#         fg.add_child(marker)
#     city_map_obj = st_folium(city_map, width=900, height=400)
    # marker = folium.Marker(
    #     location=[5.621085071, -0.215586875],
    #     popup=Popup("test", parse_html=False),
    #     tooltip="Tooltip!"
    # )
    # marker.add_to(st.session_state.city_map)
    #
    # city_map_obj = st_folium(st.session_state.city_map, width=900, height=400)
    # # st.session_state.city_map.render()
    # m = folium.Map(location=[5.621085071, -0.215586875], zoom_start=8)
    # fg = folium.FeatureGroup(name="Markers")
    # for marker in st.session_state["markers"]:
    #     fg.add_child(marker)
    #
    # st_folium(
    #     m,
    #     center=st.session_state["center"],
    #     zoom=st.session_state["zoom"],
    #     key="new",
    #     feature_group_to_add=fg,
    #     height=400,
    #     width=700,
    # )

