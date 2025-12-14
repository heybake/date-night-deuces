import streamlit as st

st.set_page_config(page_title="Airport Protocol", page_icon="✈️")

st.markdown("""
# 🧬 The Airport Protocol: Wallet Card

### 1. THE VACUUM CHECK (First 15 Hands)
* **Trigger:** Bankroll drops 25% (to $30)
* **Action:** 🛑 HARD STOP LOSS.

---

### 2. THE TEASE (Sub-Surface Check)
* **Trigger:** You spike profit, but lose it all within 5 hands.
* **Action:** 🛑 EXIT IMMEDIATELY.

---

### 3. THE ZOMBIE ZONE (Hand 40)
* **Trigger:** You are "Underwater" (<$40) but not dead.
* **Action:** ⏱️ SET TIMER (5 Mins Max). Do NOT grind.

---

### 4. THE HARD DECK (Hand 66)
* **Trigger:** Hand 66 reached with no win.
* **Action:** 🛑 WALK AWAY. (Math Dead)

---

### 🎯 THE SNIPER EXCEPTION (WIN)
* **Trigger:** Hit +20% Profit ($48.00+)
* **Action:** 💰 CASH OUT. (Volatility Win)
""")

st.divider()
st.page_link("streamlit_app.py", label="⬅️ Back to Game", icon="🔙")