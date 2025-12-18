import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE CONFIG ---
st.set_page_config(page_title="AgroHydrology Lab: Runoff Tool", layout="wide")

# --- TITLE & CONTEXT ---
st.title("💧 AgroHydrology Decision Support System")
st.markdown(
    """
**Objective:** Calibrate the SCS-Curve Number parameter for **Houston Black Clay**.
**Method:** Adjust the sliders to match the *Model (Red)* with *Reality (Black)*.
"""
)


# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Update path to your clean file
    file_path = "/Users/albarka/Desktop/GRA/data/Cleaned_Data.csv"
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    # Filter 2008-2009 only
    df = df[df["Date"].dt.year >= 2008]
    df = df.sort_values("Date")
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Data Error: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Calibration Controls")

# 1. Curve Number Slider
cn_input = st.sidebar.slider(
    "Curve Number (CN)", 60, 95, 84, help="Higher = More Runoff (Impermeable)"
)

# 2. Climate Scenario Checkbox
st.sidebar.subheader("🌍 Climate Stress Test")
climate_change = st.sidebar.checkbox("Simulate +20% Rainfall Intensity")

# Apply Climate Change if checked
rainfall_data = df["Rainfall"] * 1.2 if climate_change else df["Rainfall"]

# --- MODEL CALCULATION (Live) ---
S = (1000 / cn_input) - 10
Ia = 0.2 * S
df["Simulated_Runoff"] = np.where(
    rainfall_data > Ia, ((rainfall_data - Ia) ** 2) / (rainfall_data - Ia + S), 0
)

# Metrics
rmse = np.sqrt(((df["Measured_Runoff"] - df["Simulated_Runoff"]) ** 2).mean())
total_obs = df["Measured_Runoff"].sum()
total_sim = df["Simulated_Runoff"].sum()
vol_error = ((total_sim - total_obs) / total_obs) * 100

# --- MAIN DASHBOARD ---

# Row 1: Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current CN", f"{cn_input}")
col2.metric("RMSE (Accuracy)", f"{rmse:.3f}", delta_color="inverse")  # Lower is better
col3.metric("Total Observed Vol", f"{total_obs:.1f} in")
col4.metric("Volume Error", f"{vol_error:+.1f}%", delta_color="inverse")

# --- PROFESSIONAL PLOT (Combo Chart) ---
# We use a "secondary_y" to show Rain and Runoff together
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 1. Rainfall (Inverted Bars on Top) - The "Hyetograph"
fig.add_trace(
    go.Bar(
        x=df["Date"],
        y=rainfall_data,
        name="Rainfall (in)",
        marker_color="blue",
        opacity=0.3,
    ),
    secondary_y=True,
)

# 2. Measured Runoff (Black Line)
fig.add_trace(
    go.Scatter(
        x=df["Date"],
        y=df["Measured_Runoff"],
        name="Measured Runoff",
        line=dict(color="black", width=3),
        opacity=0.7,
    ),
    secondary_y=False,
)

# 3. Simulated Runoff (Red Dashed)
fig.add_trace(
    go.Scatter(
        x=df["Date"],
        y=df["Simulated_Runoff"],
        name=f"Model (CN={cn_input})",
        line=dict(color="red", width=2, dash="dash"),
    ),
    secondary_y=False,
)

# Layout Formatting
fig.update_layout(
    title="Hydrologic Response: Rainfall vs. Runoff",
    height=600,
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1),
)

# Axis 1: Runoff (Left)
fig.update_yaxes(title_text="Runoff (inches)", secondary_y=False)

# Axis 2: Rainfall (Right) - INVERTED to look like sky rain
# We set range [Max*3, 0] so bars hang from the top
max_rain = rainfall_data.max()
fig.update_yaxes(
    title_text="Rainfall (inches)", range=[max_rain * 3, 0], secondary_y=True
)

st.plotly_chart(fig, use_container_width=True)

# --- EXPLANATION ---
st.info(
    """
**How to read this chart:** The **Blue Bars** hanging from the top show Rainfall events. 
The **Lines** show how the soil responds. 
Notice how small rain events (Blue) produce ZERO runoff until the soil is saturated? 
This is the **"Initial Abstraction"** effect of the Clay soil.
"""
)
