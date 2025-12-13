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
            "Wild Royal": 25 if variant == "NSUD" else 20, 
            "5 of a Kind": 16 if variant == "NSUD" else 12,
            "Straight Flush": 10 if variant == "NSUD" else 9,
            "4 of a Kind": 4, 
            "Full House": 4 if variant == "NSUD" else 4,
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
            
            if self.variant == "AIRPORT" and current_rank == "Flush":
                 return hand, "Defensive: Hold Flush."
                 
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
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Shoot for Wild Royal."
            
            for combo in itertools.combinations(non_deuces, 3):
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
            credits = self.paytable.get(rank_name, 0)
            total_payout += credits
            
        avg_credits = total_payout / iterations
        return avg_credits * 5 

# ==========================================
# 🎨 STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Amy Bot Advisor", page_icon="🦆")

st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    .big-font { font-size:30px !important; font-weight: bold; }
    .stat-box { font-size:18px; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG ---
denoms = [0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 5.00]

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    variant_input = st.selectbox("Game Variant", ["NSUD (Aggressive)", "AIRPORT (Defensive)"])
    selected_variant = "NSUD" if "NSUD" in variant_input else "AIRPORT"
    
    if 'denom' not in st.session_state: st.session_state.denom = 0.05
    try:
        default_idx = denoms.index(st.session_state.denom)
    except ValueError:
        default_idx = 2

    denom_input = st.selectbox("Denomination", denoms, index=default_idx)
    st.session_state.denom = denom_input
    
    if 'bankroll' not in st.session_state: st.session_state.bankroll = 100.00
    st.session_state.bankroll = st.number_input("Bankroll ($)", value=st.session_state.bankroll, step=1.00)
    
    # NEW: Track Start Bankroll for Profit Calc
    if 'start_bank' not in st.session_state: st.session_state.start_bank = 100.00
    
    st.divider()
    st.info(f"Strategy: {selected_variant}")
    st.info(f"Bet Size: ${denom_input * 5:.2f}")

engine = DeucesWildEngine(variant=selected_variant)

if 'history' not in st.session_state: st.session_state.history = deque(maxlen=10) # For Amy Gauge
if 'full_history' not in st.session_state: st.session_state.full_history = [] # For Scorecard

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
    try:
        current_step = denoms.index(st.session_state.denom)
        window_size = 10 if current_step <= 2 else 5 
        recent_wins = wins[-window_size:] if len(wins) >= window_size else wins
        recent_total = len(recent_wins)
        
        if recent_total >= window_size:
            ratio = sum(recent_wins) / recent_total
            if ratio >= 0.5:
                if current_step < len(denoms) - 1:
                    recommendation = f"🔥 HEAT UP! (${denoms[current_step+1]:.2f})"
                else:
                    recommendation = "🚀 MAX LEVEL!"
            else:
                if current_step > 0:
                    recommendation = f"❄️ COOL DOWN (${denoms[current_step-1]:.2f})"
        else:
            recommendation = "Collecting Data..."
    except ValueError:
        recommendation = "Custom Denom"

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
        best_hold, reason = engine.get_best_hold(clean_hand)
        with st.spinner("Simulating..."):
            ev_val = engine.calculate_monte_carlo_ev(best_hold)
        
        st.markdown("---")
        st.subheader(f"Strategy: {reason}")
        st.caption(f"📈 EV: {ev_val:.2f} Credits (${ev_val * st.session_state.denom:.2f})")
        
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
    
    # 1. Big Buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ I WON", type="primary"):
            st.session_state.history.append(1)
            st.session_state.full_history.append(1)
            st.session_state.bankroll += st.session_state.denom * 5 
            st.rerun()
            
    with c2:
        if st.button("❌ I LOST"):
            st.session_state.history.append(0)
            st.session_state.full_history.append(0)
            st.session_state.bankroll -= st.session_state.denom * 5
            st.rerun()

    # 2. Session Stats
    st.markdown("---")
    total_hands = len(st.session_state.full_history)
    total_wins = sum(st.session_state.full_history)
    win_rate = (total_wins / total_hands * 100) if total_hands > 0 else 0.0
    profit = st.session_state.bankroll - st.session_state.start_bank
    
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Hands", total_hands)
    s2.metric("Win Rate", f"{win_rate:.0f}%")
    s3.metric("Profit/Loss", f"${profit:+.2f}")
    
    # 3. The 5-Hand Grid (Scorecard)
    st.subheader("📜 History (5-Hand Cycles)")
    
    # Display in reverse order (newest on top) or sequential? 
    # Usually sequential is better for reading a scorecard.
    
    history_list = st.session_state.full_history
    if not history_list:
        st.caption("No hands logged yet.")
    else:
        # Loop in chunks of 5
        for i in range(0, len(history_list), 5):
            batch = history_list[i : i+5]
            batch_str = " ".join(["✅" if x==1 else "❌" for x in batch])
            
            # Labeling the range (e.g. "Hands 1-5")
            st.text(f"Hands {i+1}-{i+len(batch)}:  {batch_str}")

    st.markdown("---")
    if st.button("🗑️ Reset Session Data"):
        st.session_state.bankroll = 100.00
        st.session_state.start_bank = 100.00
        st.session_state.history.clear()
        st.session_state.full_history.clear()
        st.rerun()
