"""Router: run this file.  streamlit run app.py"""
import streamlit as st
from common import apply_theme
 
st.set_page_config(page_title="Road Accident Insights", page_icon="🚗", layout="wide")
apply_theme()
 
pages = st.navigation(
    [
        st.Page("overview_page.py", title="Overview", icon="📊", default=True),
        st.Page("urban_rural_page.py", title="Urban or Rural", icon="🏙️"),
        st.Page("compare_counties_page.py", title="Compare Counties", icon="⚖️"),
    ]
)
pages.run()