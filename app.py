import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Athlete Energy Tracker", layout="wide")

st.title("Athlete Energy Balance System")

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "meals" not in st.session_state:
    st.session_state.meals = []

if "activities" not in st.session_state:
    st.session_state.activities = []

# -----------------------------
# FOOD DATABASE (simple model)
# -----------------------------
food_db = {
    "chicken": {"cal": 165},
    "rice": {"cal": 130},
    "beef": {"cal": 250},
    "egg": {"cal": 70},
    "milk": {"cal": 60},
    "coke": {"cal": 140},
    "banana": {"cal": 105},
    "apple": {"cal": 95},
    "fish": {"cal": 140},
}

# -----------------------------
# ACTIVITY BURN RATES (cal/min)
# -----------------------------
activity_db = {
    "running": 10,
    "football": 12,
    "walking": 4,
    "cycling": 8,
    "gym": 6
}

# -----------------------------
# MOVING AVERAGE FUNCTION
# -----------------------------
def moving_avg(series, window=3):
    return series.rolling(window=window).mean()

# -----------------------------
# FOOD INPUT
# -----------------------------
st.header("Log Meal")

meal_input = st.text_input("Enter food (comma separated)")

if st.button("Add Meal"):
    items = [x.strip().lower() for x in meal_input.split(",")]

    total_cal = 0

    for item in items:
        if item in food_db:
            total_cal += food_db[item]["cal"]

    st.session_state.meals.append({
        "time": datetime.now().strftime("%H:%M"),
        "cal": total_cal
    })

    st.success("Meal added")

# -----------------------------
# ACTIVITY INPUT
# -----------------------------
st.header("Log Activity")

activity = st.text_input("Activity (e.g. running, football)")
minutes = st.number_input("Duration (minutes)", min_value=0)

if st.button("Add Activity"):
    if activity in activity_db and minutes > 0:
        burn = activity_db[activity] * minutes

        st.session_state.activities.append({
            "time": datetime.now().strftime("%H:%M"),
            "burn": burn
        })

        st.success("Activity added")
    else:
        st.warning("Invalid activity or time")

# -----------------------------
# DATAFRAMES
# -----------------------------
food_df = pd.DataFrame(st.session_state.meals)
act_df = pd.DataFrame(st.session_state.activities)

# -----------------------------
# ENERGY BALANCE GRAPH
# -----------------------------
if not food_df.empty or not act_df.empty:

    # fill missing time alignment
    all_times = sorted(
        set(food_df["time"].tolist() if not food_df.empty else []) |
        set(act_df["time"].tolist() if not act_df.empty else [])
    )

    df = pd.DataFrame({"time": all_times})

    # merge food
    if not food_df.empty:
        df = df.merge(food_df.groupby("time")["cal"].sum(), on="time", how="left")
        df.rename(columns={"cal": "cal_in"}, inplace=True)
    else:
        df["cal_in"] = 0

    # merge activity
    if not act_df.empty:
        df = df.merge(act_df.groupby("time")["burn"].sum(), on="time", how="left")
        df.rename(columns={"burn": "cal_out"}, inplace=True)
    else:
        df["cal_out"] = 0

    df = df.fillna(0)

    # MOVING AVERAGES
    df["cal_in_ma"] = moving_avg(df["cal_in"])
    df["cal_out_ma"] = moving_avg(df["cal_out"])

    # -----------------------------
    # GRAPH
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["cal_in_ma"],
        mode="lines+markers",
        name="Calories In (MA)",
        line=dict(color="green")
    ))

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["cal_out_ma"],
        mode="lines+markers",
        name="Calories Burned (MA)",
        line=dict(color="red")
    ))

    fig.update_layout(
        title="Energy Balance (Smoothed)",
        dragmode="zoom"
    )

    fig.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "editInChartStudio"]
        }
    )

else:
    st.info("Start logging meals and activities")
