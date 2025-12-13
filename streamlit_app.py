import streamlit as st
import itertools
import random
from collections import deque

# ==========================================
# 🧬 CORE LOGIC: DEUCES WILD ENGINE
# ==========================================
class DeucesWildEngine:
    def __init__(self, variant="NSUD"):
        self.variant = variant
        self.paytable = {
            "Natural Royal": 800, "Four Deuces": 200, "Wild Royal": 25,
            "5 of a Kind": 16 if variant == "NSUD" else 12,
            "Straight Flush": 10 if variant == "NSUD" else 9,
            "4 of a Kind": 4, "Full House": 4, "Flush": 3, "Straight": 2, "3 of a Kind": 1, "Nothing": 0
        }

    def get_rank_val(self, card):
        r = card[:-1] 
        mapping = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        return mapping.get(r, 0)

    def evaluate_hand(self, hand):
        ranks = [c[:-1] for c in hand]
        suits = [c[-1] for c in hand]
        deuces = ranks.count('2')
        non_deuce_ranks = sorted([self.get_rank_val(c) for c in hand if c[:-1] != '2'])
        is_flush = len(set(suits)) == 1
        
        if is_flush and deuces == 0 and set(ranks) == {'10','J','Q','K','A'}: return "Natural Royal"
        if deuces == 4: return "Four Deuces"
        if is_flush and deuces > 0 and set(non_deuce_ranks).issubset({10,11,12,13,14}): return "Wild Royal"
        
        counts = {x:non_deuce_ranks.count(x) for x in set(non_deuce_ranks)}
        max_k = max(counts.values()) if counts else 0
        
        if deuces + max_k >= 5: return "5 of a Kind"
        if is_flush:
            if not non_deuce_ranks or (non_deuce_ranks[-1] - non_deuce_ranks[0] <= 4): return "Straight Flush"
            if 14 in non_deuce_ranks and (non_deuce_ranks[0] == 5): return "Straight Flush" # Simple Wheel check

        if deuces + max_k >= 4: return "4 of a Kind"
        if deuces == 0 and 3 in counts.values() and 2 in counts.values(): return "Full House"
        if is_flush: return "Flush"
        
        unique_vals = sorted(list(set(non_deuce_ranks)))
        if len(unique_vals) + deuces >= 5:
            if unique_vals[-1] - unique_vals[0] <= 4: return "Straight"
            if 14 in unique_vals and unique_vals[0] <= 5: return "Straight" # Simple Wheel check
            
        if deuces + max_k >= 3: return "3 of a Kind"
        return "Nothing"

    def get_best_hold(self, hand):
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
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Hunt the Wild Royal."
            if self.variant == "AIRPORT" and current_rank == "Flush": return hand, "Defensive: Hold Flush."
            return deuces, "Hold 2 Deuces."
            
        # --- 1 Deuce ---
        if len(deuces) == 1:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush", "Full House"]: return hand, "Hold Made Hand."
            if current_rank == "4 of a Kind": return hand, "Hold Quads."
            if self.variant == "AIRPORT":
                if current_rank == "Flush": return hand, "Defensive: Hold Flush."
                if current_rank == "Straight": return hand, "Defensive: Hold Straight."

            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 3):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return deuces + list(combo), "Shoot for Wild Royal."
            
            for combo in itertools.combinations(non_deuces, 3):
                 vals = sorted([self.get_rank_val(c) for c in combo])
                 suits = [c[-1] for c in combo]
                 if len(set(suits)) == 1 and (vals[-1] - vals[0] <= 4): return deuces + list(combo), "Straight Flush Draw."

            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return deuces + list(combo), "3 to Wild Royal."
            return deuces, "Hold Deuce."

        # --- 0 Deuces ---
        if len(deuces) == 0:
            if current_rank in ["Natural Royal", "Straight Flush", "4 of a Kind", "Full House", "Flush", "Straight", "3 of a Kind"]: 
                return hand, "Made Hand. Hold."
            
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 4):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return list(combo), "4 to Royal!"
            
            for combo in itertools.combinations(non_deuces, 3):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return list(combo), "3 to Royal."
            
            pairs = []
            seen = set()
            for c in hand:
                r = c[:-1]
                if r in seen: pairs.append(r)
                seen.add(r)
            if pairs:
                pair_cards = [c for c in hand if c[:-1] in pairs]
                return pair_cards, "Hold Pair."

            return [], "Trash. Redraw 5."

    def calculate_monte_carlo_ev(self, held_cards, iterations=500):
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        full_deck = [f"{r}{s}" for r in ranks for s in suits]
        for c in held_cards:
            if c in full_deck: full_deck.remove(c)
        total_payout = 0
        draw_count = 5 - len(held_cards)
        for _ in range(iterations):
            drawn = random.sample(full_deck, draw_count)
            final_hand = held_cards + drawn
            rank_name = self.evaluate_hand(final_hand)
            total_payout += self.paytable.get(rank_name, 0)
        return (total_payout / iterations) * 5 

# ==========================================
# 🎨 STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Amy Bot Lite", page_icon="🦆")

st.markdown("""
<style>
    div.stButton > button { width: 100%; height: 70px; font-size: 24px; border-radius: 12px; }
    .big-stat { font-size: 40px; font-weight: bold; text-align: center; }
    .rec-box { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;}
    .rec-hot { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .rec-cold { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Minimal) ---
with st.sidebar:
    st.header("⚙️ Config")
    variant_input = st.selectbox("Variant", ["NSUD (Aggressive)", "AIRPORT (Defensive)"])
    selected_variant = "NSUD" if "NSUD" in variant_input else "AIRPORT"
    st.info(f"Mode: {selected_variant}")

engine = DeucesWildEngine(variant=selected_variant)

if 'history' not in st.session_state: st.session_state.history = []

# --- HEADER: MOMENTUM GAUGE ---
st.title("🦆 Amy Bot: Momentum")

# Calculate Stats
total_hands = len(st.session_state.history)
wins = sum(st.session_state.history)

# Logic: Look at last 5 hands
last_5 = st.session_state.history[-5:] if total_hands >= 5 else st.session_state.history
wins_in_last_5 = sum(last_5)
count_in_last_5 = len(last_5)

# Recommendation Engine
if count_in_last_5 < 5:
    msg = f"Collecting Data ({count_in_last_5}/5)..."
    style = "rec-cold" # Default
elif wins_in_last_5 >= 3:
    msg = f"🔥 HEAT UP! ({wins_in_last_5}/5 Wins) -> CONSIDER RAISING"
    style = "rec-hot"
else:
    msg = f"❄️ COOL DOWN ({wins_in_last_5}/5 Wins) -> STAY MINIMUM"
    style = "rec-cold"

st.markdown(f"""<div class='rec-box {style}'><h3>{msg}</h3></div>""", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Scorecard (Logger)", "✋ Hand Helper"])

# ==========================================
# TAB 1: SCORECARD (The Main Tool)
# ==========================================
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ WON"):
            st.session_state.history.append(1)
            st.rerun()
    with c2:
        if st.button("❌ LOST"):
            st.session_state.history.append(0)
            st.rerun()
            
    st.divider()
    
    # VISUAL HISTORY (Grouped by 5)
    st.subheader("Session History")
    if not st.session_state.history:
        st.write("No hands played yet.")
    else:
        # Reverse loop to show newest on top? No, scorecard usually top-down.
        # Let's show "Batches"
        history = st.session_state.history
        for i in range(0, len(history), 5):
            batch = history[i : i+5]
            batch_icons = "".join(["✅ " if x==1 else "❌ " for x in batch])
            st.write(f"**Hands {i+1}-{i+len(batch)}:** {batch_icons}")

    st.markdown("---")
    if st.button("🗑️ Reset All Data"):
        st.session_state.history = []
        st.rerun()

# ==========================================
# TAB 2: HAND HELPER (Strategy)
# ==========================================
with tab2:
    st.caption("Only use for tricky hands.")
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suit_map = {'♠️':'s', '♥️':'h', '♦️':'d', '♣️':'c'}

    cols = st.columns(5)
    selected_hand = []
    clean_hand = []
    
    for i in range(5):
        with cols[i]:
            r = st.selectbox("", ranks, key=f"r{i}")
            s = st.selectbox("", suits, key=f"s{i}")
            selected_hand.append(f"{r}{s}")
            clean_hand.append(f"{r}{suit_map[s]}")
    
    if st.button("🧠 Solve"):
        best_hold, reason = engine.get_best_hold(clean_hand)
        ev_val = engine.calculate_monte_carlo_ev(best_hold, iterations=200) # Fast sim
        
        st.success(f"Strategy: {reason}")
        st.caption(f"EV: {ev_val:.2f} Credits")
        
        # Simple text display of hold
        held_display = []
        for j, c_code in enumerate(clean_hand):
            if c_code in best_hold:
                held_display.append(selected_hand[j])
        st.write(f"**HOLD:** {' '.join(held_display)}")
