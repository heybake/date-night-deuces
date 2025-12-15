import streamlit as st

def show_rules():
    st.title("📖 Airport Protocol")
    st.markdown("### The Official Variance Classifications")
    st.caption("Select a class below to see real-world examples and detection signs.")

    # 1. THE VACUUM
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown("### 1. The Vacuum")
            st.markdown("**Trigger:** Bankroll drops 25% (to $30) in first 15 hands.")
            st.markdown("🛑 **Action:** HARD STOP LOSS.")
        with c2:
            st.write("") # Spacer
            if st.button("🔍 View Profile", key="btn_vacuum"):
                st.session_state.current_view = "detail_vacuum"
                st.rerun()

    # 2. THE TEASE
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown("### 2. The Tease (Sub-Surface)")
            st.markdown("**Trigger:** You spike profit, but lose it all within 5 hands.")
            st.markdown("🛑 **Action:** EXIT IMMEDIATELY.")
        with c2:
            st.write("")
            if st.button("🔍 View Profile", key="btn_tease"):
                st.session_state.current_view = "detail_tease"
                st.rerun()

    # 3. THE ZOMBIE
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown("### 3. The Zombie")
            st.markdown("**Trigger:** 'Underwater' (<$40) at Hand 40.")
            st.markdown("⏱️ **Action:** SET TIMER (Do NOT Grind).")
        with c2:
            st.write("")
            if st.button("🔍 View Profile", key="btn_zombie"):
                st.session_state.current_view = "detail_zombie"
                st.rerun()

    # 4. THE SNIPER
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown("### 🎯 The Sniper")
            st.markdown("**Trigger:** Hit +20% Profit ($48.00+).")
            st.markdown("💰 **Action:** CASH OUT.")
        with c2:
            st.write("")
            if st.button("🔍 View Profile", key="btn_sniper"):
                st.session_state.current_view = "detail_sniper"
                st.rerun()

    # 5. HARD DECK
    with st.container(border=True):
        st.markdown("### 💀 The Hard Deck (Hand 66)")
        st.markdown("**Trigger:** Hand 66 reached with no win.")
        st.markdown("**Action:** 🛑 WALK AWAY. (Math Dead)")
