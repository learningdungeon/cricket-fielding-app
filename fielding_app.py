import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIG & SQUAD ---
st.set_page_config(page_title="Cricket Fielding Pro", layout="wide")

SQUAD = {
    "David Miller": "34", "Shadab Khan": "7", "Shaheen Afridi": "10",
    "Babar Azam": "56", "Naseem Shah": "71", "Mohammad Rizwan": "16"
}

# --- 2. GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize logs in session state with the new 'Direction' column
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=[
        'Timestamp', 'Player', 'Shirt_No', 'Direction', 'Ball_Contact', 
        'Fumble_Type', 'Throw_Target', 'Throw_Quality', 'Runs_Saved', 
        'Runs_Given', 'Stumps_Hit', 'Opportunity_Availed'
    ])

# --- 3. SIDEBAR: PLAYER SELECTION ---
st.sidebar.header("🏆 Squad List")
if 'active_player' not in st.session_state:
    st.session_state.active_player = "David Miller"

for player in SQUAD.keys():
    if st.sidebar.button(f"👤 {player}", use_container_width=True):
        st.session_state.active_player = player

selected_name = st.session_state.active_player
selected_shirt = SQUAD[selected_name]

# --- 4. LOGGING FUNCTION ---
# Updated to include 'direction'
def add_entry(direction="Cover", contact=0, fumble="None", target="None", quality="None", saved=0, given=0, hit=0, availed=0):
    new_row = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Player': selected_name,
        'Shirt_No': selected_shirt,
        'Direction': direction,
        'Ball_Contact': contact,
        'Fumble_Type': fumble,
        'Throw_Target': target,
        'Throw_Quality': quality,
        'Runs_Saved': saved,
        'Runs_Given': given,
        'Stumps_Hit': hit,
        'Opportunity_Availed': availed
    }
    
    # Update local session table
    st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_row])], ignore_index=True)
    
    # CLOUD UPDATE
    try:
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        updated_df = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.toast(f"✅ Cloud Synced: {selected_name} at {direction}")
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")

# --- 5. MAIN UI ---
st.title(f"🏏 Tracking: {selected_name} (#{selected_shirt})")

# Wagon Wheel Selector
st.subheader("📍 Ball Direction (Wagon Wheel)")
field_direction = st.select_slider(
    "Select the zone where the ball was hit:",
    options=["Third Man", "Point", "Cover", "Mid-Off", "Mid-On", "Mid-Wicket", "Square Leg", "Fine Leg"],
    value="Cover"
)

col_pick, col_throw, col_result = st.columns(3)

with col_pick:
    st.subheader("1. Pick-up")
    if st.button("✅ CLEAN PICK", use_container_width=True, type="primary"):
        add_entry(direction=field_direction, contact=1, saved=1)
    if st.button("🥜 NUTMEG", use_container_width=True):
        add_entry(direction=field_direction, contact=1, fumble="Nutmeg", given=1)
    if st.button("🖐️ BOBBLE", use_container_width=True):
        add_entry(direction=field_direction, contact=1, fumble="Bobble", given=0)

with col_throw:
    st.subheader("2. Throw")
    target_side = st.radio("Target", ["Keeper", "Non-Striker"], horizontal=True)
    if st.button("🎯 GOOD THROW", use_container_width=True):
        add_entry(direction=field_direction, contact=1, target=target_side, quality="Good")
    if st.button("⚠️ BAD THROW", use_container_width=True):
        add_entry(direction=field_direction, contact=1, target=target_side, quality="Bad", given=1)

with col_result:
    st.subheader("3. Big Plays")
    if st.button("🔥 DIRECT HIT", use_container_width=True):
        add_entry(direction=field_direction, contact=1, hit=1, availed=1, saved=1)
    if st.button("☝️ RUN OUT", use_container_width=True):
        add_entry(direction=field_direction, contact=1, availed=1)

# --- 6. STATS BUTTON ---
st.divider()
if st.button("📊 SHOW LEADERBOARD", use_container_width=True):
    st.subheader("Live Session Summary")
    try:
        summary_df = conn.read(worksheet="Sheet1", ttl=0)
        if not summary_df.empty:
            leaderboard = summary_df.groupby("Player").agg({
                'Ball_Contact': 'sum',
                'Runs_Saved': 'sum',
                'Stumps_Hit': 'sum',
                'Opportunity_Availed': 'sum'
            }).rename(columns={
                'Ball_Contact': 'Picks',
                'Runs_Saved': 'Saved',
                'Stumps_Hit': 'Hits',
                'Opportunity_Availed': 'Chances'
            })
            st.table(leaderboard)
            best_saved = leaderboard['Saved'].idxmax()
            st.success(f"🔥 Most Runs Saved: **{best_saved}**")
        else:
            st.info("The leaderboard is empty.")
    except Exception as e:
        st.error("Stats temporarily unavailable.")
