import streamlit as st
import itertools
import random
from collections import deque

# ==========================================
# 🧬 CORE LOGIC: DEUCES WILD ENGINE
# (Integrated directly so you don't need extra files)
# ==========================================

class DeucesWildEngine:
    def __init__(self, variant="NSUD"):
        self.variant = variant
        self.paytable = {
            "Natural Royal": 800, "Four Deuces": 200, "Wild Royal": 25,
            "5 of a Kind": 16 if variant == "NSUD" else 12,
            "Straight Flush": 10 if variant == "NSUD" else 9,
            "4 of a Kind": 4, "Full House": 4 if variant == "NSUD" else 4,
            "Flush": 3, "Straight": 2, "3 of a Kind": 1, "Nothing": 0
        }

    def get_rank_val(self, card):
        r = card[:-1] # Rank is everything except last char
        mapping = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        return mapping.get(r, 0)

    def evaluate_hand(self, hand):
        # Basic evaluator for 5-card hands
        ranks = [c[:-1] for c in hand]
        suits = [c[-1] for c in hand]
        deuces = ranks.count('2')
        non_deuce_ranks = sorted([self.get_rank_val(c) for c in hand if c[:-1] != '2'])
        
        is_flush = len(set(suits)) == 1
        
        # 1. Natural Royal
        if is_flush and deuces == 0 and set(ranks) == {'10','J','Q','K','A'}: return "Natural Royal"
        # 2. Four Deuces
        if deuces == 4: return "Four Deuces"
        # 3. Wild Royal
        if is_flush and deuces > 0 and set(non_deuce_ranks).issubset({10,11,12,13,14}): return "Wild Royal"
        # 4. Five of a Kind
        counts = {x:non_deuce_ranks.count(x) for x in set(non_deuce_ranks)}
        max_k = max(counts.values()) if counts else 0
        if deuces + max_k >= 5: return "5 of a Kind"
        # 5. Straight Flush
        if is_flush:
            if not non_deuce_ranks: return "Straight Flush"
            # Standard SF Check
            if (non_deuce_ranks[-1] - non_deuce_ranks[0] <= 4): return "Straight Flush"
            # Wheel Check (A-2-3-4-5) - simplified for brevity
            if 14 in non_deuce_ranks and (non_deuce_ranks[0] == 3 or non_deuce_ranks[0] == 4 or non_deuce_ranks[0] == 5): return "Straight Flush"

        if deuces + max_k >= 4: return "4 of a Kind"
        if deuces == 0 and 3 in counts.values() and 2 in counts.values(): return "Full House"
        if is_flush: return "Flush"
        
        # Straight Logic (Simplified for brevity)
        unique_vals = sorted(list(set(non_deuce_ranks)))
        if len(unique_vals) + deuces >= 5:
            if unique_vals[-1] - unique_vals[0] <= 4: return "Straight"
            
        if deuces + max_k >= 3: return "3 of a Kind"
        return "Nothing"

    def get_best_hold(self, hand):
        # A lightweight version of the optimal strategy
        # Returns (Held Cards List, Strategy Name)
        deuces = [c for c in hand if c.startswith('2')]
        non_deuces = [c for c in hand if not c.startswith('2')]
        current_rank = self.evaluate_hand(hand)
        
        # --- 4 Deuces ---
        if len(deuces) == 4: return hand, "Victory! Hold All."
        
        # --- 3 Deuces ---
        if len(deuces) == 3:
            if current_rank in ["Wild Royal", "5 of a Kind"]: return hand, "Jackpot! Hold All."
            return deuces, "Hold 3 Deuces."
            
        # --- 2 Deuces ---
        if len(deuces) == 2:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush"]: return hand, "Monster! Hold All."
            if current_rank == "4 of a Kind": return hand, "Hold Made Quads."
            # 4 to Wild Royal
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Hunt the Wild Royal."
            return deuces, "Hold 2 Deuces."
            
        # --- 1 Deuce ---
        if len(deuces) == 1:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush", "Full House"]: return hand, "Hold Made Hand."
            if current_rank == "4 of a Kind": return hand, "Hold Quads."
            # 4 to Wild Royal
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 3):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Shoot for Wild Royal."
            # 3 to Wild Royal
            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "3 to Wild Royal."
            return deuces, "Hold Deuce."

        # --- 0 Deuces ---
        if len(deuces) == 0:
            if current_rank in ["Natural Royal", "Straight Flush", "4 of a Kind", "Full House", "Flush", "Straight", "3 of a Kind"]: 
                return hand, "Made Hand. Hold."
            
            # 4 to Royal
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 4):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return list(combo), "4 to Royal!"
            
            # 3 to Royal
            for combo in itertools.combinations(non_deuces, 3):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return list(combo), "3 to Royal."
            
            # Pair
            pairs = []
            seen = set()
            for c in hand:
                r = c[:-1]
                if r in seen: pairs.append(r)
                seen.add(r)
            if pairs:
                # Find the pair cards
                pair_cards = [c for c in hand if c[:-1] in pairs]
                return pair_cards, "Hold Pair."

            return [], "Trash. Redraw 5."

# ==========================================
# 🎨 STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Amy Bot Advisor", page_icon="🦆")

# --- CSS Styling for Mobile Buttons ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'bankroll' not in st.session_state: st.session_state.bankroll = 100.00
if 'history' not in st.session_state: st.session_state.history = deque(maxlen=10)
if 'denom' not in st.session_state: st.session_state.denom = 0.05
if 'hand_input' not in st.session_state: st.session_state.hand_input = []

engine = DeucesWildEngine()

# --- HEADER: AMY'S BETTING GAUGE ---
st.title("🦆 Amy Bot Advisor")

col1, col2 = st.columns(2)
with col1:
    st.metric("Bankroll", f"${st.session_state.bankroll:.2f}")
with col2:
    # Logic for Betting Level
    wins = list(st.session_state.history)
    win_count = sum(wins)
    total_tracked = len(wins)
    
    # Amy Logic (Simplified for Dashboard)
    # Lvl 1 ($0.05) -> Needs 50% of last 10 to go up
    # Lvl 2 ($0.10) -> Needs 50% of last 5
    # Lvl 3 ($0.25) -> Needs 50% of last 3
    
    recommendation = "HOLD"
    color = "off"
    
    if st.session_state.denom == 0.05:
        if total_tracked >= 10 and (win_count / total_tracked) >= 0.5:
            recommendation = "🔥 HEAT UP! ($0.10)"
            color = "normal"
    elif st.session_state.denom == 0.10:
        recent = wins[-5:] if len(wins) >= 5 else wins
        if sum(recent)/len(recent) < 0.5:
            recommendation = "❄️ COOL DOWN ($0.05)"
            color = "inverse"
        elif len(wins) >= 10 and (sum(wins[-5:])/5) >= 0.5: # Simple heuristic
             recommendation = "🚀 MAX BET ($0.25)"
    
    st.metric("Current Denom", f"${st.session_state.denom:.2f}", recommendation)

# --- TAB SELECTION ---
tab1, tab2 = st.tabs(["✋ Hand Advisor", "💰 Session Logger"])

# ==========================================
# TAB 1: HAND ADVISOR (The "Cheat Sheet")
# ==========================================
with tab1:
    st.write("Select your cards to get optimal hold:")
    
    # Card Selector Helpers
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    # We use 5 columns for fast input
    cols = st.columns(5)
    selected_hand = []
    
    for i in range(5):
        with cols[i]:
            # Rank
            r = st.selectbox(f"R{i+1}", ranks, key=f"r{i}")
            # Suit
            s = st.selectbox(f"S{i+1}", suits, key=f"s{i}")
            selected_hand.append(f"{r}{s}")
    
    # Convert to engine format (2♠️ -> 2s)
    clean_hand = []
    for c in selected_hand:
        r = c[:-1]
        s_icon = c[-1]
        s_char = {'♠️':'s', '♥️':'h', '♦️':'d', '♣️':'c'}[s_icon]
        clean_hand.append(f"{r}{s_char}")
        
    # Analyze Button
    if st.button("🧠 Analyze Hand"):
        best_hold, reason = engine.get_best_hold(clean_hand)
        
        # Display Results
        st.markdown("---")
        st.subheader(f"Strategy: {reason}")
        
        # Visualizing Hold
        hold_cols = st.columns(5)
        for i, card in enumerate(selected_hand):
            clean_card = clean_hand[i]
            with hold_cols[i]:
                if clean_card in best_hold:
                    st.success(f"{card}\nHOLD")
                else:
                    st.error(f"{card}\nDISCARD")

# ==========================================
# TAB 2: SESSION LOGGER (Amy's Brain)
# ==========================================
with tab2:
    st.info("Tap result AFTER the draw to update the Amy Gauge.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ I WON", type="primary"):
            st.session_state.history.append(1)
            # Simple bankroll heuristic
            st.session_state.bankroll += st.session_state.denom * 5 # Approx win
            st.rerun()
            
    with c2:
        if st.button("❌ I LOST"):
            st.session_state.history.append(0)
            st.session_state.bankroll -= st.session_state.denom * 5
            st.rerun()

    st.markdown("---")
    st.write("Win History (Last 10): " + "".join(["✅" if x==1 else "❌" for x in st.session_state.history]))
    
    if st.button("Reset Session"):
        st.session_state.bankroll = 100.00
        st.session_state.history.clear()
        st.session_state.denom = 0.05
        st.rerun()
