import streamlit as st
import pandas as pd

# Set page config for mobile friendliness
st.set_page_config(page_title="Deuces Tracker", page_icon="🦆", layout="centered")

# Initialize Session State for History
if 'history' not in st.session_state:
    # 1 = Won, 0 = Lost
    st.session_state.history = []

# ============================================
# 🎨 CUSTOM CSS FOR BIG BUTTONS
# ============================================
# This CSS targets the buttons inside the specific columns we create later.
# It makes them tall, bold, and gives them distinct winning/losing colors.
st.markdown("""
<style>
    /* General styling for the big buttons */
    .big-button {
        width: 100%;
        height: 100px !important; /* Force height */
        font-size: 32px !important; /* Force big text */
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }

    /* Specific styling for the WON button column */
    div[data-testid="column"]:nth-of-type(1) .stButton button {
        background-color: #28a745 !important; /* Green */
        color: white !important;
    }
    div[data-testid="column"]:nth-of-type(1) .stButton button:hover {
         background-color: #1e7e34 !important; /* Darker Green hover */
         transform: scale(1.02);
    }

    /* Specific styling for the LOST button column */
    div[data-testid="column"]:nth-of-type(2) .stButton button {
         background-color: #dc3545 !important; /* Red */
         color: white !important;
    }
    div[data-testid="column"]:nth-of-type(2) .stButton button:hover {
         background-color: #bd2130 !important; /* Darker Red hover */
         transform: scale(1.02);
    }
    
    /* Styling for metrics to make them pop */
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 🧮 CALCULATE MOMENTUM METRICS
# ============================================
history = st.session_state.history
total_hands = len(history)
total_wins = sum(history)

# Helper function to calculate percentage safely
def calculate_pct(wins, total):
    return (wins / total * 100) if total > 0 else 0.0

# 1. Overall Game
overall_pct = calculate_pct(total_wins, total_hands)

# 2. Last 10 Hands
last_10 = history[-10:]
hands_in_last_10 = len(last_10)
wins_in_last_10 = sum(last_10)
last_10_pct = calculate_pct(wins_in_last_10, hands_in_last_10)

# 3. Last 5 Hands
last_5 = history[-5:]
hands_in_last_5 = len(last_5)
wins_in_last_5 = sum(last_5)
last_5_pct = calculate_pct(wins_in_last_5, hands_in_last_5)


# ============================================
# 📊 THE NEW DASHBOARD UI
# ============================================
st.title("🦆 Deuces Momentum")

# Display Metrics in a row
m1, m2, m3, m4 = st.columns(4)

# Metric 1: Clear Total Hand Count
m1.metric("Total Hands", total_hands)

# Metric 2: Entire Game Win %
m2.metric("Overall Win %", f"{overall_pct:.1f}%")

# Metric 3: Last 10 Win %
# We add a help tooltip to show the exact fraction (e.g., 6/10)
m3.metric("Last 10", f"{last_10_pct:.1f}%", help=f"{wins_in_last_10} wins out of {hands_in_last_10} hands")

# Metric 4: Last 5 Win %
# Visual trick: color the metric based on heat
delta_color = "off"
if hands_in_last_5 >= 5:
    if wins_in_last_5 >= 4: delta_color = "normal" # Green/Hot for 4+ wins
    elif wins_in_last_5 <= 1: delta_color = "inverse" # Red/Cold for 1 or less wins

m4.metric("Last 5 (Heat)", f"{last_5_pct:.0f}%", delta=None, delta_color=delta_color, help=f"{wins_in_last_5} wins out of {hands_in_last_5} hands")

st.divider()

# ============================================
# 🔴🟢 THE NEW BIG BUTTONS
# ============================================
# We use two columns. The CSS defined at the top targets these specific columns
# to apply the big green/red styling.

col_won, col_lost = st.columns(2)

with col_won:
    # We add a class name to help the CSS target it, though the column targeting does most work
    if st.button("✅ WON HAND", key="big_won", use_container_width=True):
        st.session_state.history.append(1)
        st.rerun()

with col_lost:
    if st.button("❌ LOST HAND", key="big_lost", use_container_width=True):
        st.session_state.history.append(0)
        st.rerun()


# ============================================
# 📜 HISTORY LOG (Existing functionality)
# ============================================
st.divider()
st.subheader("Session Log")

if total_hands == 0:
    st.caption("Tap the big buttons above to start tracking.")
else:
    # Display history in groups of 5, reversed so newest is top
    for i in range(total_hands, 0, -5):
        start_index = max(0, i-5)
        end_index = i
        batch = history[start_index:end_index]
        
        # Create the check/x string
        icons = "".join(["✅ " if x == 1 else "❌ " for x in batch])
        
        st.write(f"**Hands {start_index + 1}-{end_index}:** {icons}")

st.divider()

# Reset button at the bottom, styled normally so it doesn't conflict with the big buttons
if st.button("🗑️ Reset Session History"):
    st.session_state.history = []
    st.rerun()
