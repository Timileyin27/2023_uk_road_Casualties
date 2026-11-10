import pandas as pd
import streamlit as st
from common import *
 
df = get_data()
counties = sorted(df["police_force"].unique())
 
st.sidebar.header("⚖️ Compare")
name_a = st.sidebar.selectbox("County A", counties, index=counties.index("Kent"), key="cmp_a")
name_b = st.sidebar.selectbox("County B", counties, index=counties.index("Sussex"), key="cmp_b")
mode = st.sidebar.radio("Show values as", ["Number of accidents", "% of county's accidents"],
                        key="cmp_mode")
pct = mode.startswith("%")
st.sidebar.caption("Tip: use % when the two counties are very different in size.")
 
banner("County Comparison – Road Accident Insights",
       f"{name_a} vs {name_b} · UK road accidents in 2023")
 
if name_a == name_b:
    st.warning("Please choose two different counties to compare.")
    st.stop()
 
a = df[df["police_force"] == name_a]
b = df[df["police_force"] == name_b]
 
# ---------------- KPI cards (one row per county) ----------------
county_tag(name_a, COMPARE_A)
kpi_row(a)
county_tag(name_b, COMPARE_B)
kpi_row(b)
 
 
# ---------------- Key rates table ----------------
def rates(d):
    n = len(d)
    return {
        "Total accidents": f"{n:,}",
        "Total casualties": f"{int(d['number_of_casualties'].sum()):,}",
        "Casualties per accident": f"{d['number_of_casualties'].sum() / n:.2f}",
        "Fatal or serious (%)": f"{d['fatal_or_serious'].mean() * 100:.1f}%",
        "Urban accidents (%)": f"{(d['urban_or_rural_area'] == 'Urban').mean() * 100:.1f}%",
        "In darkness (%)": f"{(d['light_group'] != 'Daylight').mean() * 100:.1f}%",
        "Non-dry road surface (%)": f"{(d['surface_group'] != 'Dry').mean() * 100:.1f}%",
        "Police attended scene (%)": f"{(d['attended'] == 'Yes').mean() * 100:.1f}%",
    }
 
 
st.subheader("Key rates")
st.dataframe(pd.DataFrame({name_a: rates(a), name_b: rates(b)}), width="stretch")
 
# ---------------- Charts ----------------
def cmp(col, title, order, kind="bar"):
    return compare_chart(a, b, name_a, name_b, col, title, order, pct, kind)
 
 
c1, c2 = st.columns(2)
show(cmp("collision_severity", "Accidents by Severity", ["Slight", "Serious", "Fatal"]), c1)
show(cmp("urban_or_rural_area", "Urban vs Rural", ["Urban", "Rural"]), c2)
 
c3, c4 = st.columns(2)
show(cmp("day_of_week", "Accidents by Day of Week", DAYS), c3)
show(cmp("time_of_day", "Accidents by Time of Day", TOD_ORDER), c4)
 
show(cmp("month", "Accidents by Month", MONTHS, kind="line"))
 
c5, c6 = st.columns(2)
show(cmp("weather_group", "Accidents by Weather Conditions",
         ["Fine", "Rain", "Snow", "Fog", "Other", "Unknown"]), c5)
show(cmp("surface_group", "Accidents by Road Surface Conditions",
         ["Dry", "Wet or Damp", "Snow or Ice", "Frost or Ice", "Flood", "Unknown"]), c6)
 
c7, c8 = st.columns(2)
show(cmp("speed_label", "Accidents by Speed Limit",
         [f"{s} mph" for s in (20, 30, 40, 50, 60, 70)]), c7)
show(cmp("light_group", "Accidents by Light Conditions",
         ["Daylight", "Dark - lights lit", "Dark - no lighting",
          "Dark - lighting unknown", "Dark - lights unlit"]), c8)
 
# ---------------- Map ----------------
both = pd.concat([a.sample(min(len(a), 2500), random_state=1),
                  b.sample(min(len(b), 2500), random_state=1)])
show(location_map(both, "Accident Locations (sample of up to 2,500 points per county)",
                  max_points=10_000, color_col="police_force",
                  color_map={name_a: COMPARE_A, name_b: COMPARE_B}))
 
st.caption("Counties are taken from the police force column in the dataset.")
 