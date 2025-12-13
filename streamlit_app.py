import streamlit as st
import itertools
import random
from collections import deque
import copy

# ==========================================
# 🧬 CORE LOGIC: DEUCES WILD ENGINE
# ==========================================

class DeucesWildEngine:
    def __init__(self, variant="NSUD"):
        self.variant = variant
        self.paytable = {
            "Natural Royal": 800, 
            "Four Deuces": 200, 
            "Wild Royal": 25 if variant == "NSUD" else 20, # Variant diff
            "5 of a Kind": 16 if variant == "NSUD" else 12, # Variant diff
            "Straight Flush": 10 if variant == "NSUD" else 9, # Variant diff
            "4 of a Kind": 4, 
            "Full House": 4 if variant == "NSUD" else 4, # Usually 4/3 or 4/4
            "Flush": 3, 
            "Straight": 2, 
            "3 of a Kind": 1, 
            "Nothing": 0
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
            if not non_deuce_ranks: return "Straight Flush"
            if (non_deuce_ranks[-1] - non_deuce_ranks[0] <= 4): return "Straight Flush"
            if 14 in non_deuce_ranks and (non_deuce_ranks[0] == 3 or non_deuce_ranks[0] == 4 or non_deuce_ranks[0] == 5): return "Straight Flush"

        if deuces + max_k >= 4: return "4 of a Kind"
        if deuces == 0 and 3 in counts.values() and 2 in counts.values(): return "Full House"
        if is_flush: return "Flush"
        
        unique_vals = sorted(list(set(non_deuce_ranks)))
        if len(unique_vals) + deuces >= 5:
            if unique_vals[-1] - unique_vals[0] <= 4: return "Straight"
            # Wheel straight check A-2-3-4-5
            if 14 in unique_vals:
                wheel_vals = [1 if x==14 else x for x in unique_vals]
                wheel_vals.sort()
                if wheel_vals[-1] - wheel_vals[0] <= 4: return "Straight"
            
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
            
            # Variant Split: Airport holds Flush, NSUD breaks it
            if self.variant == "AIRPORT" and current_rank == "Flush":
                 return hand, "Defensive: Hold Flush."
                 
            return deuces, "Hold 2 Deuces."
            
        # --- 1 Deuce ---
        if len(deuces) == 1:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush", "Full House"]: return hand, "Hold Made Hand."
            if current_rank == "4 of a Kind": return hand, "Hold Quads."
            
            # Variant Split: Airport holds Straight/Flush, NSUD often breaks
            if self.variant == "AIRPORT":
                if current_rank == "Flush": return hand, "Defensive: Hold Flush."
                if current_rank == "Straight": return hand, "Defensive: Hold Straight."

            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 3):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Shoot for Wild Royal."
            
            for combo in itertools.combinations(non_deuces, 3):
                 # Simple check for Straight Flush draw (consecutive suited)
                 vals = sorted([self.get_rank_val(c) for c in combo])
                 suits = [c[-1] for c in combo]
                 if len(set(suits)) == 1 and (vals[-1] - vals[0] <= 4):
                     return deuces + list(combo), "Straight Flush Draw."

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

    def calculate_monte_carlo_ev(self, held_cards, iterations=1000):
        # 1. Build Deck
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        full_deck = [f"{r}{s}" for r in ranks for s in suits]
        
        # 2. Remove Held Cards
        for c in held_cards:
            if c in full_deck: full_deck.remove(c)
            
        # 3. Simulate
        total_payout = 0
        draw_count = 5 - len(held_cards)
        
        for _ in range(iterations):
            drawn = random.sample(full_deck, draw_count)
            final_hand = held_cards + drawn
            rank_name = self.evaluate_hand(final_hand)
            credits = self.paytable.get(rank_name, 0)
            total_payout += credits
            
        avg_credits = total_payout / iterations
        return avg_credits * 5 # Max bet normalized

# ==========================================
# 🎨 STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Amy Bot Advisor", page_icon="🦆")

# --- CSS Styling ---
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    .big-font { font-size:30px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Variant Selector
    variant_input = st.selectbox("Game Variant", ["NSUD (Aggressive)", "AIRPORT (Defensive)"])
    selected_variant = "NSUD" if "NSUD" in variant_input else "AIRPORT"
    
    # 2. Denom Selector
    denom_input = st.selectbox("Denomination", [0.05, 0.10, 0.25, 1.00], index=0)
    
    # 3. Bankroll Editor
    if 'bankroll' not in st.session_state: st.session_state.bankroll = 100.00
    st.session_state.bankroll = st.number_input("Bankroll ($)", value=st.session_state.bankroll, step=1.00)
    
    # Store settings in session
    st.session_state.denom = denom_input
    
    st.divider()
    st.info(f"Strategy: {selected_variant}")
    st.info(f"Bet Size: ${denom_input * 5:.2f}")

# Initialize Engine with selected variant
engine = DeucesWildEngine(variant=selected_variant)

if 'history' not in st.session_state: st.session_state.history = deque(maxlen=10)

# --- HEADER: AMY'S BETTING GAUGE ---
st.title("🦆 Amy Bot Advisor")

col1, col2 = st.columns(2)
with col1:
    st.metric("Bankroll", f"${st.session_state.bankroll:.2f}")
with col2:
    wins = list(st.session_state.history)
    win_count = sum(wins)
    total_tracked = len(wins)
    
    recommendation = "HOLD"
    
    # Amy Logic
    if st.session_state.denom == 0.05:
        if total_tracked >= 10 and (win_count / total_tracked) >= 0.5:
            recommendation = "🔥 HEAT UP! ($0.10)"
    elif st.session_state.denom == 0.10:
        recent = wins[-5:] if len(wins) >= 5 else wins
        if sum(recent)/len(recent) < 0.5:
            recommendation = "❄️ COOL DOWN ($0.05)"
        elif len(wins) >= 10 and (sum(wins[-5:])/5) >= 0.5:
             recommendation = "🚀 MAX BET ($0.25)"
    
    st.metric("Current Denom", f"${st.session_state.denom:.2f}", recommendation)

# --- TABS ---
tab1, tab2 = st.tabs(["✋ Hand Advisor", "💰 Session Logger"])

# ==========================================
# TAB 1: HAND ADVISOR
# ==========================================
with tab1:
    st.write("Select your cards:")
    
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suit_map = {'♠️':'s', '♥️':'h', '♦️':'d', '♣️':'c'}

    cols = st.columns(5)
    selected_hand = []
    clean_hand = []
    
    for i in range(5):
        with cols[i]:
            r = st.selectbox(f"R{i+1}", ranks, key=f"r{i}")
            s = st.selectbox(f"S{i+1}", suits, key=f"s{i}")
            selected_hand.append(f"{r}{s}")
            clean_hand.append(f"{r}{suit_map[s]}")
    
    if st.button("🧠 Analyze Hand"):
        # 1. Get Strategy
        best_hold, reason = engine.get_best_hold(clean_hand)
        
        # 2. Calculate EV (Monte Carlo)
        with st.spinner("Simulating outcomes..."):
            ev_val = engine.calculate_monte_carlo_ev(best_hold)
        
        # 3. Display
        st.markdown("---")
        st.subheader(f"Strategy: {reason}")
        st.caption(f"📈 Expected Value (EV): {ev_val:.2f} Credits (approx ${ev_val * st.session_state.denom:.2f})")
        
        hold_cols = st.columns(5)
        for i, card_disp in enumerate(selected_hand):
            card_code = clean_hand[i]
            with hold_cols[i]:
                if card_code in best_hold:
                    st.success(f"{card_disp}\nHOLD")
                else:
                    st.error(f"{card_disp}\nDISCARD")

# ==========================================
# TAB 2: SESSION LOGGER
# ==========================================
with tab2:
    st.info("Tap result AFTER the draw.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ I WON", type="primary"):
            st.session_state.history.append(1)
            st.session_state.bankroll += st.session_state.denom * 5 
            st.rerun()
            
    with c2:
        if st.button("❌ I LOST"):
            st.session_state.history.append(0)
            st.session_state.bankroll -= st.session_state.denom * 5
            st.rerun()

    st.write("History: " + "".join(["✅" if x==1 else "❌" for x in st.session_state.history]))
    
    if st.button("Reset Session"):
        st.session_state.bankroll = 100.00
        st.session_state.history.clear()
        st.rerun()
