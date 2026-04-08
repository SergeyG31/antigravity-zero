import streamlit as st
import pandas as pd
import time
from config import STOCK_PAIRS

st.set_page_config(page_title="MEXC Specialist", layout="wide")

st.title("💎 MEXC STOCK HUB")
st.subheader("Monitoring Wall Street vs Crypto Lags")

# Build table safely
tickers = list(STOCK_PAIRS.values())
assets = list(STOCK_PAIRS.keys())

data = []
for i in range(len(tickers)):
    data.append({
        "Stock": tickers[i],
        "Token": assets[i],
        "Market Status": "Monitoring...",
        "Signal": "SCANNING"
    })

df = pd.DataFrame(data)
st.table(df)

st.sidebar.success("MEXC ORCHESTRATOR: ACTIVE")
st.sidebar.write(f"Tracking {len(tickers)} Stock Assets")

time.sleep(10)
st.rerun()
