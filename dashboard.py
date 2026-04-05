import os
import streamlit as st
from datetime import datetime
from automate_budget import create_expense_tracker
from visualize_budget import visualize_dashboard

st.set_page_config(page_title="Expense Dashboard", layout="wide")

st.title("💰 Personal Expense Dashboard")

# Dropdowns Input
current_year = datetime.now().year
years = list(range(2026, current_year + 1))

months = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

is_generate = False
is_visualize = False

@st.dialog("File Already Exists", width="medium")
def confirm_overwrite(year, month):
    st.warning(f"⚠️ {year}/{month} Expense Tracker.xlsx already exists. Overwrite?")
    _, col1, _, col2, _ = st.columns(5)
    with col1:
        if st.button("✅ Yes", width="stretch"):
            st.session_state["overwrite_confirmed"] = True
            st.rerun()
    with col2:
        if st.button("❌ No", width="stretch"):
            st.session_state["overwrite_confirmed"] = False
            st.rerun()

col1, col2 = st.columns(2)

with col1:
    year = st.selectbox("Select Year", years)

with col2:
    month = st.selectbox("Select Month", months)

# Buttons for Generate and Visualize
_, col_btn1, _, _, col_btn2, _ = st.columns(6)

with col_btn1:
    if st.button("📥 Generate", width="stretch"):
        is_generate = True
        file_path = f"{year}/{month} Expense Tracker.xlsx"
        if os.path.exists(file_path):
            # opens modal
            confirm_overwrite(year, month)
        else:
            st.session_state["overwrite_confirmed"] = True

with col_btn2:
    if st.button("📊 Visualize", width="stretch"):
        is_visualize = True

st.divider()

if st.session_state.get("overwrite_confirmed") is True:
    st.session_state["overwrite_confirmed"] = None
    create_expense_tracker(year, month)
elif st.session_state.get("overwrite_confirmed") is False:
    st.session_state["overwrite_confirmed"] = None
    st.info("Operation cancelled.")

if is_visualize and not is_generate:
    try:
        visualize_dashboard(year, month)
    finally:
        is_visualize = False

