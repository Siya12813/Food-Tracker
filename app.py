import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Athlete Performance System", layout="wide")

st.title("Athlete Nutrition + Performance System (V2)")

# -----------------------------
# SESSION STATE
# -----------------------------
if "meals" not in st.session_state:
    st.session_state.meals = []

if "activities" not in st.session_state:
    st.session_state.activities = []

# -----------------------------
# FOOD DATABASE
# -----------------------------
food_db = {
    "chicken": {"cal": 165, "p": 25, "c": 0, "f": 3, "liq": 0},
    "rice": {"cal": 130, "p": 3, "c": 28, "f": 1, "liq": 0},
    "beef": {"cal": 250, "p": 26, "c": 0, "f": 20, "liq": 0},
    "egg": {"cal": 70, "p": 6, "c": 1, "f": 5, "liq": 0},
    "milk": {"cal": 60, "p": 3, "c": 5, "f": 3, "liq": 100},
    "coke": {"cal": 140, "p": 0, "c": 39, "f": 0, "liq": 330},
    "banana": {"cal": 105, "p": 1, "c": 27, "f": 0, "liq": 0},
    "apple": {"cal": 95, "p": 0, "c": 25, "f": 0, "liq": 0},
    "fish": {"cal": 140, "p": 22, "c": 0, "f": 5, "liq": 0},
}

# -----------------------------
# ACTIVITY DATABASE
# -----------------------------
activity_db = {
    "running": 10,
    "football": 12,
    "walking": 4,
    "cycling": 8,
    "gym": 6
}

# -----------------------------
# MOVING AVERAGE
# -----------------------------
def ma(series, window=3):
    return series.rolling(window=window).mean()

# -----------------------------
# GLUCOSE MODEL (SIMPLIFIED)
# -----------------------------
def glucose_curve(calories):
    x = np.linspace(0, 10, 50)
    return calories * np.exp(-0.5 * x)

# -----------------------------
# INPUT: MEALS
# -----------------------------
st.header("Log Meal")
meal_input = st.text_input("Enter meal (comma separated)")

if st.button("Add Meal"):
    items = [x.strip().lower() for x in meal_input.split(",")]

    totals = {"cal":0,"p":0,"c":0,"f":0,"liq":0}

    for i in items:
        if i in food_db:
            for k in totals:
                totals[k] += food_db[i][k]

    st.session_state.meals.append({
        "time": datetime.now().strftime("%H:%M"),
        **totals
    })

    st.success("Meal added")

# -----------------------------
# INPUT: ACTIVITY
# -----------------------------
st.header("Log Activity")

activity = st.text_input("Activity")
minutes = st.number_input("Minutes", min_value=0)

if st.button("Add Activity"):
    if activity in activity_db:
        burn = activity_db[activity] * minutes

        st.session_state.activities.append({
            "time": datetime.now().strftime("%H:%M"),
            "burn": burn
        })

        st.success("Activity added")

# -----------------------------
# DATAFRAMES
# -----------------------------
df = pd.DataFrame(st.session_state.meals)
adf = pd.DataFrame(st.session_state.activities)

if not df.empty or not adf.empty:

    # merge time axis
    times = sorted(set(
        df["time"].tolist() if not df.empty else []
    ) | set(
        adf["time"].tolist() if not adf.empty else []
    ))

    base = pd.DataFrame({"time": times})

    # FOOD
    if not df.empty:
        f = df.groupby("time").sum().reset_index()
        base = base.merge(f, on="time", how="left")
    else:
        base["cal"] = 0
        base["p"] = 0
        base["c"] = 0
        base["f"] = 0
        base["liq"] = 0

    # ACTIVITY
    if not adf.empty:
        a = adf.groupby("time")["burn"].sum().reset_index()
        base = base.merge(a, on="time", how="left")
    else:
        base["burn"] = 0

    base = base.fillna(0)

    # MOVING AVG
    base["cal_ma"] = ma(base["cal"])
    base["burn_ma"] = ma(base["burn"])
    base["liq_ma"] = ma(base["liq"])

    # -----------------------------
    # ENERGY GRAPH
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=base["time"], y=base["cal_ma"], name="Calories IN", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=base["time"], y=base["burn_ma"], name="Calories OUT", line=dict(color="red")))

    fig.update_layout(title="Energy Balance (Smoothed)", dragmode="zoom")
    fig.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # MACRO PIE CHART
    # -----------------------------
    fig2 = go.Figure(data=[go.Pie(
        labels=["Protein","Carbs","Fat"],
        values=[base["p"].sum(), base["c"].sum(), base["f"].sum()]
    )])

    fig2.update_layout(title="Macro Breakdown")
    st.plotly_chart(fig2)

    # -----------------------------
    # ENERGY PIE
    # -----------------------------
    fig3 = go.Figure(data=[go.Pie(
        labels=["Energy In","Energy Out"],
        values=[base["cal"].sum(), base["burn"].sum()]
    )])

    fig3.update_layout(title="Energy Balance Ratio")
    st.plotly_chart(fig3)

    # -----------------------------
    # LIQUID GRAPH
    # -----------------------------
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=base["time"],
        y=base["liq_ma"],
        name="Liquids (ml)",
        mode="lines+markers"
    ))

    fig4.update_layout(title="Hydration Over Time")
    st.plotly_chart(fig4)

    # -----------------------------
    # GLUCOSE CURVE
    # -----------------------------
    fig5 = go.Figure()

    fig5.add_trace(go.Scatter(
        y=glucose_curve(base["cal"].sum()),
        name="Glucose Response"
    ))

    fig5.update_layout(title="Estimated Glucose Curve")
    st.plotly_chart(fig5)

    # -----------------------------
    # SIMPLE RECOMMENDATION
    # -----------------------------
    st.subheader("Next Meal Recommendation")

    if base["p"].sum() < base["c"].sum():
        st.write("Increase protein intake (chicken, fish, eggs)")
    else:
        st.write("Balanced intake maintained")

else:
    st.info("Start logging meals and activities")
