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

MOMENTUM_THRESHOLD = 0.0004  # 0.04% (Ultra High Sensitivity)
EXIT_PROFIT_TARGET = 0.0025  # 0.25% Net
STOP_LOSS_LIMIT = -0.035     # -3.5% (Sell to save the dollar)
MAX_TRADE_SIZE = 10.0        
MAX_CONCURRENT_TRADES = 5    
MEXC_TAKER_FEE = 0.001       

# AI Confirmation & Safety
MIN_AI_SCORE = 5             
SCAN_TIMEOUT = 5             
GLOBAL_MARKET_GUARD = True   # AI Crash Detection

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
