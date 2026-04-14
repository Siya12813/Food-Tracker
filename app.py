import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Food + Energy Tracker", layout="wide")

st.title("Food + Energy Tracker (Student Athlete Mode)")

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# -----------------------------
# INPUT SECTION
# -----------------------------
st.header("Log Food")

col1, col2, col3 = st.columns(3)

with col1:
    food = st.text_input("Food name")

with col2:
    grams = st.number_input("Amount (grams)", min_value=0.0)

with col3:
    food_type = st.selectbox("Type", ["Protein", "Carbs", "Fat"])

if st.button("Add Food Entry"):
    if food and grams > 0:
        # SIMPLE calorie model (approx)
        calorie_map = {
            "Protein": 4,
            "Carbs": 4,
            "Fat": 9
        }

        calories = grams * calorie_map[food_type]

        st.session_state.data.append({
            "time": datetime.now().strftime("%H:%M"),
            "food": food,
            "grams": grams,
            "type": food_type,
            "calories": calories
        })

        st.success("Added!")
    else:
        st.warning("Enter valid food and grams")

# -----------------------------
# DATA DISPLAY
# -----------------------------
df = pd.DataFrame(st.session_state.data)

if not df.empty:
    st.subheader("Food Log")
    st.dataframe(df)

    # -----------------------------
    # BAR CHART (Calories in)
    # -----------------------------
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["time"],
        y=df["calories"],
        name="Calories In"
    ))

    fig.update_layout(title="Calories Intake Over Time")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # PIE CHART (Macros)
    # -----------------------------
    macro_totals = df.groupby("type")["grams"].sum()

    fig2 = go.Figure(data=[go.Pie(
        labels=macro_totals.index,
        values=macro_totals.values
    )])

    fig2.update_layout(title="Macro Distribution")
    st.plotly_chart(fig2)

    # -----------------------------
    # SIMPLE ENERGY MODEL (FIXED FOR NOW)
    # -----------------------------
    st.subheader("Energy Burn (Estimated)")

    st.write("Running + football + walking estimated burn curve")

    energy_burn = [200, 400, 600, 500, 700]  # simplified example timeline

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        y=energy_burn,
        mode="lines+markers",
        name="Energy Burn"
    ))

    fig3.update_layout(title="Energy Burn Over Time")
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Start logging food to see graphs")
