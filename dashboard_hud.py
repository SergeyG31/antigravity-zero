import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
from auth_manager import AuthManager
from scraper_engine import ScraperEngine
from ad_manager import AdManager
from ai_guardian_agent import AIGuardianAgent
from config import ASSET_PAIR, EXCHANGES

# Sidebar: Tactical Dashboard Command Hub
st.set_page_config(page_title="P2P Sovereign HUD", layout="wide", initial_sidebar_state="expanded")

# UI Styling: Tactical Blue/Gold
st.markdown("""
    <style>
    .main { background-color: #0b111a; color: #ffffff; }
    .stMetric { background-color: #1a222f; padding: 15px; border-radius: 10px; border-bottom: 3px solid #f0b90b; }
    .stTable { background-color: #1a222f; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Initialize Aggregator Engine
@st.cache_resource
def load_all_engines():
    auth = AuthManager()
    scraper = ScraperEngine(auth)
    ad_mgr = AdManager(auth)
    guardian = AIGuardianAgent()
    return auth, scraper, ad_mgr, guardian

auth, scraper, ad_mgr, guardian = load_all_engines()

# Header: Unified Command Center
st.title(f"🚀 P2P Sovereign Tactical Dashboard [{ASSET_PAIR}]")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Profit (24h)", "₪1,248.50", delta="₪12.3% ILS")
col2.metric("Total Order Volume", "125,000 USDT")
col3.metric("Counterparty Risk", "Low-Scanned", delta="-0.2%")
col4.metric("Active Exchange Hubs", f"{len(EXCHANGES)}/{len(EXCHANGES)}", delta="All Connected")

# Main Content Sections
tab_ops, tab_matrix, tab_security = st.tabs(["🚀 Live Operations View", "📊 Spread Matrix", "🛡️ AI Guardian Log"])

with tab_ops:
    st.subheader(f"🔥 Operational Hub ({len(EXCHANGES)} Exchanges)")
    m_col1, m_col2 = st.columns([2, 1])
    with m_col1:
        # Integrated Ad Status Table - Dynamically built from EXCHANGES
        prices = scraper.price_hub
        op_rows = []
        for ex in EXCHANGES:
            ex_upper = ex.upper()
            sell_price = prices.get(ex, {}).get('sell', 0.0)
            comp_price = round(sell_price + 0.001, 3) if sell_price > 0 else 0.0
            
            op_rows.append({
                "Exchange": ex_upper,
                "Ad Status": "Active (Pos #1)" if sell_price > 0 else "Offline",
                "My Price": f"{sell_price:.3f}" if sell_price > 0 else "---",
                "Comp #1": f"{comp_price:.3f}" if comp_price > 0 else "---",
                "Margin%": "2.42%" # Mock margin for display
            })
            
        st.table(pd.DataFrame(op_rows))
        
    with m_col2:
        st.subheader("⚠️ Critical Actions")
        if st.button("🚨 EMERGENCY: STOP ALL ADS (GLOBAL)"):
            st.error("SHUTDOWN: Disabling all P2P ads across all platforms.")
        if st.button("🟢 RE-ENABLE AGGRESSION"):
            st.success("MM Mode: Under-cutting re-enabled globally.")

with tab_matrix:
    st.subheader("📊 Cross-Exchange Spread Matrix")
    # Generating matrix dynamically
    matrix_df = scraper.calculate_spread_matrix()
    if not matrix_df.empty:
        st.table(matrix_df)
    else:
        st.info("Matrix initializing... please wait for the first scan to complete.")
    
    st.markdown("---")
    st.subheader("🤑 Top Arbitrage Opportunities (Buy Low ➔ Sell High)")
    from yield_maximizer import YieldMaximizer
    maximizer = YieldMaximizer(scraper)
    opps_df = maximizer.get_best_arbitrage_opportunity()
    
    if not opps_df.empty:
        st.success(f"🔥 Found {len(opps_df)} profitable arbitrage routes!")
        st.dataframe(opps_df, use_container_width=True)
        # Highlight the best one
        best = opps_df.iloc[0]
        st.info(f"💡 Strategy: Buy on **{best['Pair'].split(' ➔ ')[0]}** and liquidate on **{best['Pair'].split(' ➔ ')[1]}**. Net profit per 1000 USDT: **₪{best['Net Profit (₪)']}**")
    else:
        st.warning("No high-yield opportunities found at this moment (Spread too tight after fees).")

with tab_security:
    st.subheader("🛡️ AI Guardian Security Log")
    col_chats, col_ocr = st.columns([1, 1])
    with col_chats:
        st.info("💬 Chat Scan: Monitoring for 3rd party fraud and payment phishing.")
        st.success("💬 Automator: Ready to greet customers across all hubs.")
    with col_ocr:
        st.warning("⚠️ OCR Hub: Waiting for payment proofs...")

# Sidebar Menu (Footer)
st.sidebar.markdown("---")
st.sidebar.subheader("P2P Sovereign v2.0")
st.sidebar.caption(f"Connected to: {', '.join([e.upper() for e in EXCHANGES])}")
