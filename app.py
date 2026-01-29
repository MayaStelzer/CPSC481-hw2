import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Fatal Accidents on the Eight-Thousanders",
    layout="wide"
)

# Title
st.title("Fatal Mountain Climbing Accidents on the Eight-Thousanders")

# Dataset description
st.markdown("""
### Dataset Description
This dataset records climbers who tragically lost their lives while attempting to summit the **eight-thousanders**—
the 14 mountains with elevations of at least 8,000 meters.

**Source:** Mountain Climbing Accidents Dataset  
**Columns include:** date of death, climber name, nationality, cause of death, and mountain.
""")

# Load data
df = pd.read_csv("data/mountain_climbing_accidents.csv")

# Parse dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Year"] = df["Date"].dt.year

# ===== Mountain filter (moved to main page) =====
st.subheader("Select Mountain(s)")

mountains = sorted(df["Mountain"].dropna().unique())
selected_mountains = st.multiselect(
    "Mountain(s):",
    mountains,
    default=mountains
)

# Filter data (only by mountain now)
filtered_df = df[df["Mountain"].isin(selected_mountains)]

# ===== Line chart: fatalities over time =====
fatalities_per_year = (
    filtered_df
    .groupby(["Year", "Mountain"])
    .size()
    .reset_index(name="Fatalities")
)

fig_line = px.line(
    fatalities_per_year,
    x="Year",
    y="Fatalities",
    color="Mountain",
    markers=True,
    title="Fatalities Over Time on the Eight-Thousanders",
    labels={
        "Year": "Year",
        "Fatalities": "Number of Fatalities"
    },
    height=600
)

st.plotly_chart(fig_line, use_container_width=True)

# ===== Pie charts section =====
st.subheader("Distribution of Fatalities")

col1, col2 = st.columns(2)

# Pie chart: Nationality
nationality_counts = (
    filtered_df["Nationality"]
    .value_counts()
    .reset_index()
)

nationality_counts.columns = ["Nationality", "Fatalities"]

# Calculate percentage
total_fatalities = nationality_counts["Fatalities"].sum()
nationality_counts["Percentage"] = (
    nationality_counts["Fatalities"] / total_fatalities * 100
)

# Group nationalities with < 2% into "Other"
nationality_counts["Nationality"] = nationality_counts.apply(
    lambda row: row["Nationality"] if row["Percentage"] >= 2 else "Other",
    axis=1
)

# Re-aggregate after grouping
nationality_counts = (
    nationality_counts
    .groupby("Nationality", as_index=False)["Fatalities"]
    .sum()
)

fig_nationality = px.pie(
    nationality_counts,
    names="Nationality",
    values="Fatalities",
    title="Fatalities by Nationality"
)

col1.plotly_chart(fig_nationality, use_container_width=True)

# Pie chart: Mountain
mountain_counts = (
    filtered_df["Mountain"]
    .value_counts()
    .reset_index()
)

mountain_counts.columns = ["Mountain", "Fatalities"]

fig_mountain = px.pie(
    mountain_counts,
    names="Mountain",
    values="Fatalities",
    title="Fatalities by Mountain"
)

col2.plotly_chart(fig_mountain, use_container_width=True)

# ===== Question =====
st.markdown("""
### Question Explored
How do fatal climbing accidents on the eight-thousanders vary over time,
and how are these fatalities distributed across mountains and nationalities?
""")

# ===== Interpretation =====
st.markdown("""
### Interpretation
The time-series visualization highlights periods where fatalities increase
on specific mountains, potentially reflecting shifts in climbing activity,
route popularity, or environmental conditions.

The nationality pie chart shows which countries have experienced the greatest
losses, often corresponding to countries with a strong presence in high-altitude
mountaineering. The mountain pie chart highlights which peaks are associated with
the highest number of fatalities, suggesting differences in technical difficulty
and exposure to risk.
""")
