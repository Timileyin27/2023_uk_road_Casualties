
import pandas as pd
import plotly.express as px
import streamlit as st

from common import (
    get_data,
    banner,
    kpi_card,
    show,
    sum_hbar,
    sum_pie,
    casualty_heatmap,
    BLUE,
    FONT,
    NAVY,
)


# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------

df = get_data()

# Date conversion is already handled inside common.py
dmin = df["date"].min().date()
dmax = df["date"].max().date()

counties = ["All"] + sorted(df["police_force"].dropna().unique())
weathers = ["All"] + sorted(df["weather_conditions"].dropna().unique())
surfaces = ["All"] + sorted(df["road_surface_conditions"].dropna().unique())


# ------------------------------------------------------------------
# Reset filters
# ------------------------------------------------------------------

def reset_filters():
    st.session_state["ov_reset_n"] = (
        st.session_state.get("ov_reset_n", 0) + 1
    )


n = st.session_state.get("ov_reset_n", 0)


# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------

st.sidebar.header("📊 Filters")

county = st.sidebar.selectbox(
    "County (Police Force)",
    counties,
    key=f"ov_county_{n}"
)

start = st.sidebar.date_input(
    "Start date",
    value=dmin,
    min_value=dmin,
    max_value=dmax,
    format="DD/MM/YYYY",
    key=f"ov_start_{n}"
)

end = st.sidebar.date_input(
    "End date",
    value=dmax,
    min_value=dmin,
    max_value=dmax,
    format="DD/MM/YYYY",
    key=f"ov_end_{n}"
)

weather = st.sidebar.selectbox(
    "Weather conditions",
    weathers,
    key=f"ov_weather_{n}"
)

surface = st.sidebar.selectbox(
    "Road surface",
    surfaces,
    key=f"ov_surface_{n}"
)

st.sidebar.button(
    "↺ Reset filters",
    on_click=reset_filters,
    width="stretch"
)


# ------------------------------------------------------------------
# Validate date range
# ------------------------------------------------------------------

if start > end:
    start, end = end, start


# ------------------------------------------------------------------
# Filter dataset
# ------------------------------------------------------------------

fdf = df[
    (df["date"] >= pd.Timestamp(start)) &
    (df["date"] < pd.Timestamp(end) + pd.Timedelta(days=1))
]

if county != "All":
    fdf = fdf[fdf["police_force"] == county]

if weather != "All":
    fdf = fdf[fdf["weather_conditions"] == weather]

if surface != "All":
    fdf = fdf[fdf["road_surface_conditions"] == surface]


# ------------------------------------------------------------------
# Page banner
# ------------------------------------------------------------------

parts = [
    "All Counties" if county == "All" else county,
    f"{start:%d %b %Y} – {end:%d %b %Y}"
]

if weather != "All":
    parts.append(weather)

if surface != "All":
    parts.append(surface)

banner(
    "Road Accident Overview",
    "UK road accidents and casualties · " + " · ".join(parts)
)


# ------------------------------------------------------------------
# Handle empty results
# ------------------------------------------------------------------

if fdf.empty:
    st.warning(
        "No accidents match these filters. "
        "Try widening them or press Reset filters."
    )
    st.stop()


# ------------------------------------------------------------------
# KPI Cards
# ------------------------------------------------------------------

sev = fdf.groupby("collision_severity")[
    "number_of_casualties"
].sum()

k1, k2, k3, k4, k5 = st.columns(5)

kpi_card(
    k1,
    "Total Accidents",
    len(fdf),
    "kpi-blue"
)

kpi_card(
    k2,
    "Total Casualties",
    int(fdf["number_of_casualties"].sum()),
    "kpi-green"
)

kpi_card(
    k3,
    "Fatal Casualties",
    int(sev.get("Fatal", 0)),
    "kpi-dark"
)

kpi_card(
    k4,
    "Serious Casualties",
    int(sev.get("Serious", 0)),
    "kpi-red"
)

kpi_card(
    k5,
    "Slight Casualties",
    int(sev.get("Slight", 0)),
    "kpi-orange"
)

st.write("")


# ------------------------------------------------------------------
# Row 1: Monthly trend and road type
# ------------------------------------------------------------------

monthly = (
    fdf.assign(
        month_start=fdf["date"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("month_start")["number_of_casualties"]
    .sum()
    .reset_index()
)

monthly.columns = ["Month", "Casualties"]

fig_trend = px.area(
    monthly,
    x="Month",
    y="Casualties",
    markers=True
)

fig_trend.update_traces(
    line=dict(color=BLUE, width=3),
    fillcolor="rgba(31,78,180,0.25)",
    marker=dict(size=8, color=BLUE),
    hovertemplate="%{x|%b %Y}: %{y:,} casualties<extra></extra>"
)

fig_trend.update_layout(
    template="plotly_white",
    font=dict(color=FONT),
    height=400,
    hovermode="x unified",
    title=dict(
        text="Casualties – Monthly Trend",
        font=dict(size=18, color=NAVY)
    ),
    margin=dict(t=60, b=10, l=10, r=10),
    xaxis_title=None,
    yaxis_title="Casualties",
)

c1, c2 = st.columns(2)

show(fig_trend, c1)

show(
    sum_hbar(
        fdf[fdf["road_type"] != "Unknown"],
        "road_type",
        "number_of_casualties",
        "Casualties by Road Type (Top 5)"
    ),
    c2
)


# ------------------------------------------------------------------
# Row 2: Urban/Rural and Daylight/Darkness
# ------------------------------------------------------------------

light = fdf[
    fdf["light_group"].notna()
].copy()

light["light_period"] = light["light_group"].apply(
    lambda x: (
        "Daylight" if x == "Daylight"
        else "Darkness" if x.startswith("Dark -")
        else "Unknown"
    )
)

c3, c4 = st.columns(2)

show(
    sum_pie(
        fdf,
        "urban_or_rural_area",
        "number_of_casualties",
        "Casualties by Urban / Rural",
        {
            "Urban": "#1f4eb4",
            "Rural": "#2ca58d"
        },
        order=["Urban", "Rural"]
    ),
    c3
)

show(
    sum_pie(
        light,
        "light_period",
        "number_of_casualties",
        "Casualties by Daylight / Darkness",
        {
            "Daylight": "#f28e2b",
            "Darkness": "#0b1f4d",
            "Unknown": "#9e9e9e"
        },
        order=["Daylight", "Darkness", "Unknown"]
    ),
    c4
)


# ------------------------------------------------------------------
# Row 3: Accident location heatmap
# ------------------------------------------------------------------

show(
    casualty_heatmap(
        fdf,
        "Casualties by Location (Heatmap)"
    )
)


# ------------------------------------------------------------------
# Footer and filtered data
# ------------------------------------------------------------------

st.caption(
    "Casualties represent the sum of number_of_casualties. "
    "Severity represents collision severity. "
    "Counties are taken from the police force column."
)

with st.expander("View filtered data"):

    st.dataframe(
        fdf.head(1000),
        width="stretch"
    )

    st.caption(
        f"Showing first 1,000 of {len(fdf):,} rows."
    )
