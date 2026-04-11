import os
from dotenv import load_dotenv

load_dotenv()

# --- GEMINI AI CONFIG ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# --- HYPER-AGGRESSIVE MODE (MEXC ONLY) ---
TARGET_EXCHANGE = 'mexc'      
CRYPTO_PAIRS = [
    'ADA/USDT', 'CAKE/USDT', 'SHIB/USDT'
]

# --- Antigravity Hyper-Scale Settings ---
MOMENTUM_THRESHOLD = 0.0004  # 0.04%
VOLUME_MA_THRESHOLD = 1.5    # 1.5x volume spike
BTC_MOMENTUM_LIMIT = -0.0015 # -0.15% in 30s (Crash protection)
EXIT_PROFIT_TARGET = 0.0025  # 0.25% Net
STOP_LOSS_LIMIT = -0.035     
MAX_TRADE_SIZE = 10.0        
MAX_CONCURRENT_TRADES = 5    

# AI & Interval Settings
MIN_AI_SCORE = 7             
SCAN_TIMEOUT = 5             
INTELLIGENCE_RECON_INTERVAL = 60 
GLOBAL_MARKET_GUARD = True   

# Technical Strategic Settings
RSI_BUY_THRESHOLD = 35       # Oversold
RSI_SELL_THRESHOLD = 65      # Overbought
BOLLINGER_WINDOW = 20        # Standard 20 periods
BOLLINGER_STD = 2            # Standard 2 sigmas
TIMEFRAME = '1m'             # Decision timeframe
MEXC_TAKER_FEE = 0.001       

# --- API Keys (Stored in .env) ---
MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')

# --- Intelligence & Safety ---
SHADOW_MODE = False
SAFETY_MODE = True
TRADE_HISTORY_FILE = 'crypto_trade_history.json'
INSIGHTS_LOG_FILE = 'crypto_insights.log'

# Hub Settings
EXCHANGES = ['mexc']
FEE_MATRIX = {'mexc': {'maker': 0.0, 'taker': 0.001}}
