import streamlit as st
from common import *
 
df = get_data()
 
st.sidebar.header("🏙️ Filters")
selected = st.sidebar.selectbox("Area Type", ["All", "Urban", "Rural"], key="area_filter")
fdf = df if selected == "All" else df[df["urban_or_rural_area"] == selected]
 
banner("Urban or Rural – Road Accident Insights",
       f"Exploring the conditions associated with UK road accidents in 2023 · "
       f"{'Urban and Rural Areas' if selected == 'All' else selected + ' Areas'}")
kpi_row(fdf)
 
c1, c2 = st.columns(2)
show(pie(fdf, "day_of_week", "Accidents by Day of Week", DAY_COLORS, order=DAYS), c1)
show(pie(fdf, "month", "Accidents by Month (% of each month)", MONTH_COLORS, order=MONTHS, hole=0), c2)
 
c3, c4 = st.columns(2)
show(hbar(fdf, "police_force", "Top 10 Counties by Accidents"), c3)
show(pie(fdf, "time_of_day", "Accidents by Time of Day", TOD_COLORS, order=TOD_ORDER, hole=0), c4)
 
c5, c6 = st.columns(2)
show(bar(fdf, "weather_group", "Accidents by Weather Conditions",
         order=["Fine", "Rain", "Snow", "Fog", "Other", "Unknown"]), c5)
show(bar(fdf, "surface_group", "Accidents by Road Surface Conditions",
         order=["Dry", "Wet or Damp", "Snow or Ice", "Frost or Ice", "Flood", "Unknown"]), c6)
 
st.caption("Counties are taken from the police force column in the dataset.")
with st.expander("View filtered data"):
    st.dataframe(fdf.head(1000), width="stretch")
    st.caption(f"Showing first 1,000 of {len(fdf):,} rows.")
 