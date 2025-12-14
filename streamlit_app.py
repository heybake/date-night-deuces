import streamlit as st
import itertools
import random
import pandas as pd
from collections import deque, defaultdict

# ==========================================
# 🧬 CORE LOGIC: DEUCES WILD ENGINE
# ==========================================
class DeucesWildEngine:
    def __init__(self, variant="NSUD", custom_paytable=None):
        self.variant = variant
        
        # 1. Define Paytable
        if custom_paytable:
            self.paytable = custom_paytable
            # Royal Guard: Forces Natural Royal to 800
            if self.paytable.get("Natural Royal", 0) < 800:
                self.paytable["Natural Royal"] = 800
            five_oak_val = self.paytable.get("5 of a Kind", 12)
            self.strategy_mode = "DEFENSIVE" if five_oak_val < 15 else "AGGRESSIVE"
        else:
            self.paytable = {
                "Natural Royal": 800, "Four Deuces": 200, "Wild Royal": 25,
                "5 of a Kind": 16 if variant == "NSUD" else 12,
                "Straight Flush": 10 if variant == "NSUD" else 9,
                "4 of a Kind": 4, "Full House": 4, "Flush": 3, "Straight": 2, "3 of a Kind": 1, "Nothing": 0
            }
            if variant == "AIRPORT":
                self.paytable.update({"Wild Royal": 20, "5 of a Kind": 12, "Straight Flush": 9})
                self.strategy_mode = "DEFENSIVE"
            else:
                self.strategy_mode = "AGGRESSIVE"

    def get_rank_val(self, card):
        r = card[:-1].upper()
        if r == 'T': r = '10'
        mapping = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        return mapping.get(r, 0)

    def evaluate_hand(self, hand):
        ranks = [c[:-1] for c in hand]
        deuces = ranks.count('2')
        non_deuce_ranks = sorted([self.get_rank_val(c) for c in hand if c[:-1] != '2'])
        
        # Fixed: Ignore suits of Deuces
        non_deuce_suits = [c[-1] for c in hand if c[:-1] != '2']
        if not non_deuce_suits: 
            is_flush = True 
        else:
            is_flush = len(set(non_deuce_suits)) == 1

        if is_flush and deuces == 0 and set(ranks) == {'10','J','Q','K','A'}: return "Natural Royal"
        if deuces == 4: return "Four Deuces"
        if is_flush and deuces > 0 and set(non_deuce_ranks).issubset({10,11,12,13,14}): return "Wild Royal"
        
        counts = {x:non_deuce_ranks.count(x) for x in set(non_deuce_ranks)}
        max_k = max(counts.values()) if counts else 0
        if deuces + max_k >= 5: return "5 of a Kind"
        
        if is_flush:
            if deuces > 0:
                if not non_deuce_ranks: return "Straight Flush"
                span = non_deuce_ranks[-1] - non_deuce_ranks[0]
                if span <= 4: return "Straight Flush"
                if 14 in non_deuce_ranks:
                    wheel_ranks = [x for x in non_deuce_ranks if x != 14]
                    if not wheel_ranks or (wheel_ranks[-1] <= 5): return "Straight Flush"
            else:
                if (non_deuce_ranks[-1] - non_deuce_ranks[0] == 4): return "Straight Flush"
                if set(non_deuce_ranks) == {14,2,3,4,5}: return "Straight Flush"

        if deuces + max_k >= 4: return "4 of a Kind"
        if deuces == 0 and 3 in counts.values() and 2 in counts.values(): return "Full House"
        if is_flush: return "Flush"
        
        unique_vals = sorted(list(set(non_deuce_ranks)))
        if len(unique_vals) + deuces >= 5:
            if unique_vals[-1] - unique_vals[0] <= 4: return "Straight"
            if 14 in unique_vals:
                wheel_vals = [x for x in unique_vals if x != 14]
                if not wheel_vals or (wheel_vals[-1] <= 5): return "Straight"
            
        if deuces + max_k >= 3: return "3 of a Kind"
        return "Nothing"

    def get_best_hold(self, hand):
        deuces = [c for c in hand if c.startswith('2')]
        non_deuces = [c for c in hand if not c.startswith('2')]
        current_rank = self.evaluate_hand(hand)
        
        if len(deuces) == 4: return hand, "Victory! Hold All."
        
        if len(deuces) == 3:
            if current_rank in ["Wild Royal", "5 of a Kind"]: return hand, "Jackpot! Hold All."
            return deuces, "Hold 3 Deuces."
            
        if len(deuces) == 2:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush"]: return hand, "Monster! Hold All."
            if current_rank == "4 of a Kind": return hand, "Hold Made Quads."
            royals = {10,11,12,13,14}
            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals):
                    return deuces + list(combo), "Hunt the Wild Royal."
            if self.strategy_mode == "DEFENSIVE" and current_rank == "Flush": return hand, "Defensive: Hold Flush."
            return deuces, "Hold 2 Deuces."
            
        if len(deuces) == 1:
            if current_rank in ["Wild Royal", "5 of a Kind", "Straight Flush", "Full House"]: return hand, "Hold Made Hand."
            if current_rank == "4 of a Kind": return hand, "Hold Quads."
            if self.strategy_mode == "DEFENSIVE":
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
                 if len(set(suits)) == 1:
                     if (vals[-1] - vals[0] <= 4): return deuces + list(combo), "Straight Flush Draw."
                     if 14 in vals:
                         wheel_v = [x for x in vals if x!=14]
                         if wheel_v and wheel_v[-1] <= 5: return deuces + list(combo), "Straight Flush Draw."

            for combo in itertools.combinations(non_deuces, 2):
                vals = {self.get_rank_val(c) for c in combo}
                suits = {c[-1] for c in combo}
                if len(suits) == 1 and vals.issubset(royals): return deuces + list(combo), "3 to Wild Royal."
            return deuces, "Hold Deuce."

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

    def calculate_outcome_probs(self, held_cards, iterations=2000):
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        full_deck = [f"{r}{s}" for r in ranks for s in suits]
        for c in held_cards:
            if c in full_deck: full_deck.remove(c)
            
        total_payout = 0
        counts = defaultdict(int)
        draw_count = 5 - len(held_cards)
        
        for _ in range(iterations):
            drawn = random.sample(full_deck, draw_count)
            final_hand = held_cards + drawn
            rank_name = self.evaluate_hand(final_hand)
            counts[rank_name] += 1
            total_payout += self.paytable.get(rank_name, 0)
            
        ev = (total_payout / iterations) * 5
        probs = {k: v/iterations for k, v in counts.items()}
        return ev, probs

# ==========================================
# 🎨 STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Amy Bot Lite", page_icon="🦆")

st.markdown("""
<style>
    div.stButton > button { width: 100%; height: 70px; font-size: 24px; border-radius: 12px; }
    .rec-box { padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;}
    .rec-hot { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .rec-cold { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>
""", unsafe_allow_html=True)

# --- 💡 THE POP-UP RULES (Dialog) ---
@st.dialog("🧬 The Airport Protocol: Wallet Card")
def show_rules():
    st.markdown("""
    **1. THE VACUUM CHECK (First 15 Hands)**
    * **Trigger:** Bankroll drops 25% (to $30)
    * **Action:** 🛑 HARD STOP LOSS.
    
    ---
    
    **2. THE TEASE (Sub-Surface Check)**
    * **Trigger:** You spike profit, but lose it all within 5 hands.
    * **Action:** 🛑 EXIT IMMEDIATELY.
    
    ---
    
    **3. THE ZOMBIE ZONE (Hand 40)**
    * **Trigger:** You are "Underwater" (<$40) but not dead.
    * **Action:** ⏱️ SET TIMER (5 Mins Max). Do NOT grind.
    
    ---
    
    **4. THE HARD DECK (Hand 66)**
    * **Trigger:** Hand 66 reached with no win.
    * **Action:** 🛑 WALK AWAY. (Math Dead)
    
    ---
    
    **🎯 THE SNIPER EXCEPTION (WIN)**
    * **Trigger:** Hit +20% Profit ($48.00+)
    * **Action:** 💰 CASH OUT. (Volatility Win)
    """)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Config")
    
    # 🆕 BUTTON TRIGGERS THE POP-UP
    if st.button("📖 Airport Protocol Rules"):
        show_rules()
    
    st.divider()
    
    variant_input = st.selectbox("Variant", ["NSUD (Aggressive)", "AIRPORT (Defensive)", "Custom (Edit)"])
    
    custom_pt = None
    selected_variant = "NSUD"
    if "NSUD" in variant_input: selected_variant = "NSUD"
    elif "AIRPORT" in variant_input: selected_variant = "AIRPORT"
    else: selected_variant = "Custom"
    
    if selected_variant == "Custom":
        st.warning("⚠️ Editing Paytable (1 Coin)")
        if 'custom_pt_df' not in st.session_state:
            default_data = {
                "Natural Royal": 800, "Four Deuces": 200, "Wild Royal": 20, 
                "5 of a Kind": 12, "Straight Flush": 9, "4 of a Kind": 4, 
                "Full House": 4, "Flush": 3, "Straight": 2, "3 of a Kind": 1
            }
            st.session_state.custom_pt_df = pd.DataFrame(list(default_data.items()), columns=["Hand", "Payout"])
        edited_df = st.data_editor(st.session_state.custom_pt_df, hide_index=True, key="pt_editor")
        custom_pt = dict(zip(edited_df["Hand"], edited_df["Payout"]))
    else:
        with st.expander("📊 View Paytable"):
            temp_engine = DeucesWildEngine(selected_variant)
            pt_data = {"Hand": list(temp_engine.paytable.keys()), "1 Coin": list(temp_engine.paytable.values())}
            st.dataframe(pd.DataFrame(pt_data), hide_index=True)
            
    st.info(f"Mode: {selected_variant}")

engine = DeucesWildEngine
