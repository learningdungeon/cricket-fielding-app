import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="Cricket Fielding Pro", layout="wide")

if 'logs' not in st.session_state:
    # Initializing columns exactly matching your spreadsheet image
    st.session_state.logs = pd.DataFrame(columns=[
        'Timestamp', 'Player', 'Ball_Contact', 'Fumble_Type', 
        'Throw_Target', 'Throw_Quality', 'Runs_Saved', 'Runs_Given',
        'Stumps_Hit', 'Opportunity_Availed'
    ])

# --- SIDEBAR: PLAYER SELECTION ---
st.sidebar.header("Match Settings")
player_name = st.sidebar.selectbox("Active Fielder", ["David Miller", "Shadab Khan", "Glenn Maxwell"])
shirt_no = st.sidebar.text_input("Shirt No.", "10")

# --- MAIN INTERFACE ---
st.title(f"🏏 Tracking: {player_name} (#{shirt_no})")

# Helper function to log data
def add_entry(contact=0, fumble="None", target="None", quality="None", saved=0, given=0, hit=0, availed=0):
    new_row = {
        'Timestamp': datetime.now().strftime("%H:%M:%S"),
        'Player': f"{player_name} ({shirt_no})",
        'Ball_Contact': contact,
        'Fumble_Type': fumble,
        'Throw_Target': target,
        'Throw_Quality': quality,
        'Runs_Saved': saved,
        'Runs_Given': given,
        'Stumps_Hit': hit,
        'Opportunity_Availed': availed
    }
    st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_row])], ignore_index=True)
    st.toast(f"Logged action for {player_name}!")

# --- UI LAYOUT: THREE-COLUMN ACTION SYSTEM ---
col_pick, col_throw, col_result = st.columns(3)

with col_pick:
    st.subheader("1. The Pick-up")
    if st.button("✅ CLEAN PICK-UP", use_container_width=True):
        add_entry(contact=1, saved=1)
    
    st.divider()
    st.caption("Fumbles")
    if st.button("🥜 NUTMEG (Between Legs)", use_container_width=True):
        add_entry(contact=1, fumble="Nutmeg", given=1)
    if st.button("🖐️ BOBBLE", use_container_width=True):
        add_entry(contact=1, fumble="Bobble", given=0)

with col_throw:
    st.subheader("2. The Throw")
    target = st.radio("Target", ["Wicket Keeper", "Non-Striker"], horizontal=True)
    
    if st.button("🎯 GOOD THROW", use_container_width=True):
        add_entry(contact=1, target=target, quality="Good")
    
    if st.button("⚠️ BAD THROW", use_container_width=True):
        add_entry(contact=1, target=target, quality="Bad")

with col_result:
    st.subheader("3. Big Plays")
    if st.button("🔥 DIRECT HIT", use_container_width=True):
        add_entry(contact=1, hit=1, availed=1)
    
    if st.button("☝️ RUN OUT ASSIST", use_container_width=True):
        add_entry(contact=1, availed=1)

# --- DATA VIEW & EXPORT ---
st.divider()
st.subheader("Live Session Data")
st.dataframe(st.session_state.logs.tail(10), use_container_width=True)

if not st.session_state.logs.empty:
    csv = st.session_state.logs.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export to CSV (Spreadsheet)", csv, "fielding_data.csv", "text/csv")