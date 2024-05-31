import streamlit as st

import data_helper

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