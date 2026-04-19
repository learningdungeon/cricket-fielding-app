import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & SQUAD ---
st.set_page_config(page_title="Cricket Fielding Pro", layout="wide")

SQUAD = {
    "David Miller": "34",
    "Shadab Khan": "7",
    "Shaheen Afridi": "10",
    "Babar Azam": "56",
    "Naseem Shah": "71",
    "Mohammad Rizwan": "16"
}

if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=[
        'Timestamp', 'Player', 'Shirt_No', 'Ball_Contact', 'Fumble_Type', 
        'Throw_Target', 'Throw_Quality', 'Runs_Saved', 'Runs_Given',
        'Stumps_Hit', 'Opportunity_Availed'
    ])

# --- 2. SIDEBAR: ONE-TAP PLAYER SELECTION ---
st.sidebar.header("🏆 Squad List")

if 'active_player' not in st.session_state:
    st.session_state.active_player = "David Miller"

# Create a button for every player
for player in SQUAD.keys():
    if st.sidebar.button(f"👤 {player}", use_container_width=True):
        st.session_state.active_player = player

# Assign correctly for use in the rest of the app
selected_name = st.session_state.active_player
selected_shirt = SQUAD[selected_name]

st.sidebar.divider()
st.sidebar.success(f"Tracking: {selected_name} (#{selected_shirt})")

# --- 3. MAIN INTERFACE ---
st.title(f"🏏 Tracking: {selected_name} (#{selected_shirt})")

def add_entry(contact=0, fumble="None", target="None", quality="None", saved=0, given=0, hit=0, availed=0):
    new_row = {
        'Timestamp': datetime.now().strftime("%H:%M:%S"),
        'Player': selected_name, # Fixed variable name
        'Shirt_No': selected_shirt, # Fixed variable name
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
    st.toast(f"Saved: {selected_name}")

# --- 4. ACTION GRID ---
col_pick, col_throw, col_result = st.columns(3)

with col_pick:
    st.subheader("1. Pick-up")
    if st.button("✅ CLEAN PICK", use_container_width=True, type="primary"):
        add_entry(contact=1, saved=1)
    
    st.divider()
    if st.button("🥜 NUTMEG", use_container_width=True):
        add_entry(contact=1, fumble="Nutmeg", given=1)
    if st.button("🖐️ BOBBLE", use_container_width=True):
        add_entry(contact=1, fumble="Bobble", given=0)

with col_throw:
    st.subheader("2. Throw")
    target_side = st.radio("Target", ["Keeper", "Non-Striker"], horizontal=True)
    
    if st.button("🎯 GOOD THROW", use_container_width=True):
        add_entry(contact=1, target=target_side, quality="Good")
    
    if st.button("⚠️ BAD THROW", use_container_width=True):
        add_entry(contact=1, target=target_side, quality="Bad", given=1)

with col_result:
    st.subheader("3. Big Plays")
    if st.button("🔥 DIRECT HIT", use_container_width=True):
        add_entry(contact=1, hit=1, availed=1, saved=1)
    
    if st.button("☝️ RUN OUT", use_container_width=True):
        add_entry(contact=1, availed=1)

# --- 5. VIEW & EXPORT ---
st.divider()
st.dataframe(st.session_state.logs.tail(10), use_container_width=True)

if not st.session_state.logs.empty:
    csv = st.session_state.logs.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "match_data.csv", "text/csv", use_container_width=True)