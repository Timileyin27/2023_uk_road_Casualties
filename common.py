"""Shared theme, data loading and chart helpers used by every dashboard page."""
import math
import pandas as pd
import plotly.express as px
import streamlit as st
 
# ------------------------------------------------------------------
# Colours
# ------------------------------------------------------------------
NAVY = "#0b1f4d"
BLUE = "#1f4eb4"
FONT = "#1c2a4a"
 
DAY_COLORS = ["#1f4eb4", "#f28e2b", "#2ca58d", "#8e5ea2", "#17a2b8", "#0b2a6f", "#7fb3f5"]
MONTH_COLORS = ["#0b2a6f", "#1f4eb4", "#3d7ee0", "#7fb3f5", "#17a2b8", "#2ca58d",
                "#7ac28a", "#f2c14e", "#f28e2b", "#e4572e", "#b5467a", "#6b4c9a"]
HOUR_COLORS = px.colors.sample_colorscale("Twilight", [i / 24 for i in range(24)])
TOD_COLORS = {"Night (00-05)": "#0b1f4d", "Morning (06-11)": "#f2c14e",
              "Afternoon (12-17)": "#f28e2b", "Evening (18-23)": "#8e5ea2"}
SEVERITY_COLORS = {"Slight": "#f2a03d", "Serious": "#e4572e", "Fatal": "#a4161a"}
BAR_SCALE = ["#9ec5f4", "#1f4eb4", "#0b1f4d"]
COMPARE_A = "#1f4eb4"
COMPARE_B = "#f28e2b"
 
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
TOD_ORDER = ["Night (00-05)", "Morning (06-11)", "Afternoon (12-17)", "Evening (18-23)"]
 
WEATHER_MAP = {
    "Fine no high winds": "Fine", "Fine + high winds": "Fine",
    "Raining no high winds": "Rain", "Raining + high winds": "Rain",
    "Snowing no high winds": "Snow", "Snowing + high winds": "Snow",
    "Fog or mist": "Fog", "Other": "Other", "Unknown": "Unknown",
}
SURFACE_MAP = {
    "Dry": "Dry", "Wet or damp": "Wet or Damp", "Snow": "Snow or Ice",
    "Frost or ice": "Frost or Ice", "Flood over 3cm. deep": "Flood",
    "unknown (self reported)": "Unknown",
}
LIGHT_MAP = {
    "Daylight": "Daylight",
    "Darkness - lights lit": "Dark - lights lit",
    "Darkness - no lighting": "Dark - no lighting",
    "Darkness - lighting unknown": "Dark - lighting unknown",
    "Darkness - lights unlit": "Dark - lights unlit",
}
 
 
# ------------------------------------------------------------------
# Theme (call once, from the router)
# ------------------------------------------------------------------
def apply_theme():
    st.markdown(
        """
        <style>
        .stApp { background: #eef2f9; }
        .block-container { padding-top: 1rem; }
        section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b1f4d 0%, #14346f 100%); }
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] label p,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span,
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span { color: #ffffff !important; }
        section[data-testid="stSidebar"] button {
            background: #ffffff; border-radius: 8px; border: none; }
        section[data-testid="stSidebar"] button p { color: #0b1f4d !important; font-weight: 700; }
        .banner {
            background: linear-gradient(100deg, #0b1f4d 0%, #1b3f8a 60%, #2f6bd0 100%);
            padding: 20px 28px; border-radius: 12px; color: white; margin-bottom: 14px;
            box-shadow: 0 4px 14px rgba(11,31,77,.25);
        }
        .banner h1 { margin: 0; font-size: 2rem; color: white; }
        .banner p { margin: 4px 0 0 0; font-style: italic; opacity: .92; color: #dbe7ff; }
        .kpi {
            border-radius: 12px; padding: 14px 18px; border-left: 6px solid;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
        }
        .kpi .label { font-size: .85rem; font-weight: 600; opacity: .85; }
        .kpi .value { font-size: 1.9rem; font-weight: 700; }
        .kpi-blue   { background: #ffffff; color: #0b1f4d; border-color: #1f4eb4; }
        .kpi-green  { background: #ffffff; color: #0f5a45; border-color: #2ca58d; }
        .kpi-orange { background: #ffffff; color: #8a4b0f; border-color: #f2a03d; }
        .kpi-red    { background: #ffffff; color: #9a2a1a; border-color: #e4572e; }
        .kpi-dark   { background: #ffffff; color: #5c0f1f; border-color: #a4161a; }
        .county-tag {
            display: inline-block; color: white; font-weight: 700; font-size: 1rem;
            padding: 4px 16px; border-radius: 20px; margin: 4px 0 8px 0;
        }
        div[data-testid="stPlotlyChart"] {
            background: #ffffff; border-radius: 12px; padding: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
 
 
# ------------------------------------------------------------------
# Data
# ------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "cleaned_dataset_2.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    try:
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    except ValueError:
        df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
    df["weather_group"] = df["weather_conditions"].map(WEATHER_MAP).fillna("Other")
    df["surface_group"] = df["road_surface_conditions"].map(SURFACE_MAP).fillna("Unknown")
    df["light_group"] = df["light_conditions"].map(LIGHT_MAP).fillna("Unknown")
    df["attended"] = df["did_police_officer_attend_scene_of_accident"].where(
        df["did_police_officer_attend_scene_of_accident"].isin(["Yes", "No"]), "No (self-reported)"
    )
    df["speed_label"] = df["speed_limit"].astype(str) + " mph"
    df["month"] = pd.Categorical(df["month"], categories=MONTHS, ordered=True)
    df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=DAYS, ordered=True)
    df["time_of_day"] = pd.cut(df["hour"], bins=[-1, 5, 11, 17, 23], labels=TOD_ORDER)
    return df
 
 
def get_data() -> pd.DataFrame:
    try:
        return load_data()
    except FileNotFoundError:
        st.error("Could not find `cleaned_dataset_2.csv`. Put it in the same folder as app.py.")
        st.stop()
 
 
# ------------------------------------------------------------------
# Layout pieces
# ------------------------------------------------------------------
def banner(title: str, subtitle: str):
    st.markdown(
        f'<div class="banner"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
 
 
def _kpi(col, label, value, css):
    col.markdown(
        f'<div class="kpi {css}"><div class="label">{label}</div>'
        f'<div class="value">{value:,}</div></div>',
        unsafe_allow_html=True,
    )
 
 
kpi_card = _kpi
 
 
def kpi_row(fdf: pd.DataFrame):
    k1, k2, k3, k4, k5 = st.columns(5)
    _kpi(k1, "Total Accidents", len(fdf), "kpi-blue")
    _kpi(k2, "Total Casualties", int(fdf["number_of_casualties"].sum()), "kpi-green")
    _kpi(k3, "Slight Accidents", int((fdf["collision_severity"] == "Slight").sum()), "kpi-orange")
    _kpi(k4, "Serious Accidents", int((fdf["collision_severity"] == "Serious").sum()), "kpi-red")
    _kpi(k5, "Fatal Accidents", int((fdf["collision_severity"] == "Fatal").sum()), "kpi-dark")
    st.write("")
 
 
def show(fig, col=None):
    (col or st).plotly_chart(fig, width="stretch", theme=None)
 
 
# ------------------------------------------------------------------
# Chart helpers
# ------------------------------------------------------------------
def _counts(data, col, order=None):
    counts = data[col].value_counts().reset_index()
    counts.columns = [col, "Accidents"]
    if order is not None:
        counts[col] = pd.Categorical(counts[col], categories=order, ordered=True)
        counts = counts.sort_values(col)
    return counts
 
 
def pie(data, names, title, colors, order=None, hole=0.45, height=420):
    counts = _counts(data, names, order)
    fig = px.pie(
        counts, names=names, values="Accidents", hole=hole, color=names,
        color_discrete_sequence=colors if isinstance(colors, list) else None,
        color_discrete_map=colors if isinstance(colors, dict) else None,
    )
    fig.update_traces(
        sort=False, textinfo="percent", textposition="inside",
        marker=dict(line=dict(color="white", width=2)), textfont=dict(color="white", size=13),
        hovertemplate="%{label}<br>%{value:,} accidents (%{percent})<extra></extra>",
    )
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT),
        title=dict(text=title, font=dict(size=18, color=NAVY)),
        height=height, margin=dict(t=60, b=10, l=10, r=10),
        annotations=[dict(text=f"{len(data):,}<br>Total", x=0.5, y=0.5,
                          font_size=14, showarrow=False)] if hole else [],
    )
    return fig
 
 
def bar(data, col, title, order=None, height=360):
    counts = _counts(data, col, order)
    if order is None:
        counts = counts.sort_values("Accidents", ascending=False)
    fig = px.bar(counts, x=col, y="Accidents", text="Accidents", color="Accidents",
                 color_continuous_scale=BAR_SCALE)
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT), coloraxis_showscale=False,
        title=dict(text=title, font=dict(size=18, color=NAVY)), height=height,
        margin=dict(t=60, b=10, l=10, r=10), xaxis_title=None, yaxis_title=None,
    )
    return fig
 
 
def hbar(data, col, title, top_n=10, height=420):
    """Horizontal 'Top N' bar chart, biggest at the top."""
    counts = _counts(data, col).sort_values("Accidents", ascending=False).head(top_n)
    counts = counts.sort_values("Accidents")
    fig = px.bar(counts, x="Accidents", y=col, text="Accidents", orientation="h",
                 color="Accidents", color_continuous_scale=BAR_SCALE)
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT), coloraxis_showscale=False,
        title=dict(text=title, font=dict(size=18, color=NAVY)), height=height,
        margin=dict(t=60, b=10, l=10, r=40), xaxis_title=None, yaxis_title=None,
    )
    return fig
 
 
def location_map(data, title, max_points=5000, height=520,
                 color_col="collision_severity", color_map=None):
    """Scatter map of accident locations, coloured by `color_col`."""
    color_map = color_map or SEVERITY_COLORS
    sample = data if len(data) <= max_points else data.sample(max_points, random_state=1)
    lat_lo, lat_hi = data["latitude"].quantile([0.02, 0.98])
    lon_lo, lon_hi = data["longitude"].quantile([0.02, 0.98])
    span = max(lat_hi - lat_lo, lon_hi - lon_lo, 0.01)
    zoom = max(3.5, min(12, 8.8 - math.log2(span)))
    orders = {"collision_severity": ["Slight", "Serious", "Fatal"]} if color_col == "collision_severity" else {}
    fig = px.scatter_map(
        sample, lat="latitude", lon="longitude", color=color_col,
        color_discrete_map=color_map, category_orders=orders,
        hover_data={"road_type": True, "speed_limit": True, "latitude": False, "longitude": False},
        zoom=zoom, center=dict(lat=data["latitude"].median(), lon=data["longitude"].median()),
        map_style="carto-positron", opacity=0.7,
    )
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        font=dict(color=FONT), height=height, margin=dict(t=60, b=10, l=10, r=10),
        title=dict(text=title, font=dict(size=18, color=NAVY)),
        legend=dict(title=None, orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
    )
    return fig
 
 
# ------------------------------------------------------------------
# County comparison helpers
# ------------------------------------------------------------------
def county_tag(name, color):
    st.markdown(f'<span class="county-tag" style="background:{color}">{name}</span>',
                unsafe_allow_html=True)
 
 
def compare_chart(a, b, name_a, name_b, col, title, order, pct=False, kind="bar", height=380):
    """Grouped bars (or lines) putting two counties side by side."""
    frames = []
    for name, d in ((name_a, a), (name_b, b)):
        s = d[col].astype(str).value_counts().reindex([str(o) for o in order], fill_value=0)
        vals = s / s.sum() * 100 if (pct and s.sum()) else s
        frames.append(pd.DataFrame({col: s.index, "County": name, "Value": vals.values}))
    long = pd.concat(frames)
    cmap = {name_a: COMPARE_A, name_b: COMPARE_B}
    if kind == "line":
        fig = px.line(long, x=col, y="Value", color="County", markers=True, color_discrete_map=cmap)
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
    else:
        fig = px.bar(long, x=col, y="Value", color="County", barmode="group", text="Value",
                     color_discrete_map=cmap)
        fig.update_traces(texttemplate="%{text:.1f}%" if pct else "%{text:,}", textposition="outside")
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT), height=height,
        title=dict(text=title, font=dict(size=18, color=NAVY)),
        margin=dict(t=70, b=10, l=10, r=10), xaxis_title=None,
        yaxis_title="% of county's accidents" if pct else "Accidents",
        legend=dict(title=None, orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
    )
    return fig
 
 
# ------------------------------------------------------------------
# Overview helpers (casualty-based charts)
# ------------------------------------------------------------------
def sum_pie(data, names, value, title, colors, order=None, hole=0.55, height=400,
            center_label="Casualties"):
    """Donut of the SUM of `value` per category (e.g. casualties by urban/rural)."""
    sums = data.groupby(names, observed=True)[value].sum().reset_index()
    sums.columns = [names, "Total"]
    if order is not None:
        sums[names] = pd.Categorical(sums[names], categories=order, ordered=True)
        sums = sums.sort_values(names)
    fig = px.pie(sums, names=names, values="Total", hole=hole, color=names,
                 color_discrete_map=colors)
    fig.update_traces(
        sort=False, textinfo="percent", textposition="inside",
        marker=dict(line=dict(color="white", width=2)), textfont=dict(color="white", size=13),
        hovertemplate="%{label}<br>%{value:,} " + center_label.lower() + " (%{percent})<extra></extra>",
    )
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT),
        title=dict(text=title, font=dict(size=18, color=NAVY)),
        height=height, margin=dict(t=60, b=10, l=10, r=10),
        annotations=[dict(text=f"{int(sums['Total'].sum()):,}<br>{center_label}", x=0.5, y=0.5,
                          font_size=14, showarrow=False)],
    )
    return fig
 
 
def sum_hbar(data, col, value, title, top_n=5, height=400, label="Casualties"):
    """Horizontal 'Top N' bar of the SUM of `value` per category, biggest on top."""
    sums = (data.groupby(col, observed=True)[value].sum().reset_index()
            .rename(columns={value: label}).sort_values(label, ascending=False).head(top_n)
            .sort_values(label))
    fig = px.bar(sums, x=label, y=col, text=label, orientation="h",
                 color=label, color_continuous_scale=BAR_SCALE)
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        template="plotly_white", font=dict(color=FONT), coloraxis_showscale=False,
        title=dict(text=title, font=dict(size=18, color=NAVY)), height=height,
        margin=dict(t=60, b=10, l=10, r=50), xaxis_title=None, yaxis_title=None,
    )
    return fig
 
 
def casualty_heatmap(data, title, weight="number_of_casualties", max_points=30_000, height=520):
    """Density heat-map of where casualties happened."""
    sample = data if len(data) <= max_points else data.sample(max_points, random_state=1)
    lat_lo, lat_hi = data["latitude"].quantile([0.02, 0.98])
    lon_lo, lon_hi = data["longitude"].quantile([0.02, 0.98])
    span = max(lat_hi - lat_lo, lon_hi - lon_lo, 0.01)
    zoom = max(3.5, min(12, 8.8 - math.log2(span)))
    fig = px.density_map(
        sample, lat="latitude", lon="longitude", z=weight, radius=14,
        center=dict(lat=data["latitude"].median(), lon=data["longitude"].median()),
        zoom=zoom, map_style="carto-positron",
        color_continuous_scale=["rgba(31,78,180,0)", "#7fb3f5", "#f2c14e", "#f28e2b", "#e4572e", "#a4161a"],
    )
    fig.update_layout(
        font=dict(color=FONT), height=height, margin=dict(t=60, b=10, l=10, r=10),
        title=dict(text=title, font=dict(size=18, color=NAVY)),
        coloraxis_showscale=False,
    )
    return fig
 