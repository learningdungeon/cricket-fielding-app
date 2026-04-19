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
    
    st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_row])], ignore_index=True)
    
    try:
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        updated_df = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.toast(f"✅ Synced: {selected_name} @ {direction}")
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")

# --- 5. MAIN UI ---
st.title(f"🏏 Tracking: {selected_name} (#{selected_shirt})")

st.subheader("📍 Wagon Wheel: Select Zone")
# Creating a layout that mimics the field
col_off, col_pitch, col_leg = st.columns([1, 0.4, 1])

with col_off:
    off_zone = st.radio("Off-Side", ["Third Man", "Point", "Cover", "Mid-Off"], index=2)

with col_pitch:
    st.markdown("<h1 style='text-align: center; margin:0;'>🏏</h1>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center;'>Pitch</p>", unsafe_allow_html=True)

with col_leg:
    leg_zone = st.radio("Leg-Side", ["Fine Leg", "Square Leg", "Mid-Wicket", "Mid-On"], index=2)

# Toggle to decide which zone is currently 'active'
side = st.radio("Side in Play", ["Off", "Leg"], horizontal=True)
field_direction = off_zone if side == "Off" else leg_zone

st.info(f"Current Zone: **{field_direction}**")

# --- ACTION BUTTONS ---
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
