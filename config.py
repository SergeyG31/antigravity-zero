import os
from dotenv import load_dotenv

load_dotenv()

# --- GEMINI AI CONFIG ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# --- HYPER-AGGRESSIVE MODE (MEXC ONLY) ---
TARGET_EXCHANGE = 'mexc'      
CRYPTO_PAIRS = [
    'CAKE/USDT', 'XRP/USDT', 'ADA/USDT', 
    'SUI/USDT', 'AVAX/USDT', 'LINK/USDT', 'MYX/USDT',
    'PEPE/USDT', 'WIF/USDT', 'BONK/USDT',
    'DOGE/USDT', 'SHIB/USDT', 'FLOKI/USDT', 
    'BOME/USDT', 'JUP/USDT', 'POPCAT/USDT'
]

# --- Aggressive Thresholds ---
MOMENTUM_THRESHOLD = 0.0008  # 0.08% (Ultra sensitive)
EXIT_PROFIT_TARGET = 0.0065  # 0.65% Net (A bit higher to capture the swing)
MAX_TRADE_SIZE = 10.0        
MAX_CONCURRENT_TRADES = 5    
MEXC_TAKER_FEE = 0.001       # 0.1%

# AI Confirmation (Aggressive)
MIN_AI_SCORE = 5             
SCAN_TIMEOUT = 5             # 5 seconds scan frequency

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
