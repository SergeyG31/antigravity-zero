import os

# --- MEXC Stock Specialist Mode ---
EXCHANGE_ID = 'mexc' # Primary exchange for Stock Tokens
ASSET_PAIRS = [] # Disabling standard crypto loops
STOCK_PAIRS = {
    'TSLAON/USDT': 'TSLA',   # Tesla
    'NVDAON/USDT': 'NVDA',   # Nvidia
    'MSFTON/USDT': 'MSFT',   # Microsoft
    'AMDON/USDT': 'AMD',     # AMD
    'MSTRON/USDT': 'MSTR',   # MicroStrategy
    'MARAON/USDT': 'MARA',   # MARA Holdings
    'SPYON/USDT': 'SPY',     # S&P 500 ETF
    'QQQON/USDT': 'QQQ',     # Nasdaq 100 ETF
    'HOODON/USDT': 'HOOD',   # Robinhood
    'MUON/USDT': 'MU',       # Micron
    'INTCON/USDT': 'INTC',   # Intel
    'TQQQON/USDT': 'TQQQ'    # UltraPro QQQ
}

MIN_LAG_THRESHOLD = 0.0015 # 0.15% Lag to ENTER
EXIT_PROFIT_TARGET = 0.0030 # 0.30% Profit to EXIT/CLOSE
MAX_TRADE_SIZE = 50.0      # Using your $50 balance

# --- API Keys (Stored in .env) ---
MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')

# --- Intelligence & Learning (Strict Additive) ---
SHADOW_MODE = True           # set to False for LIVE execution
INTELLIGENCE_RECON_INTERVAL = 300 # Deep learning scan every 5 minutes
TRADE_HISTORY_FILE = 'trade_history.json'
INSIGHTS_LOG_FILE = 'learning_insights.log'

# Fee settings for MEXC
EXCHANGES = ['mexc']
FEE_MATRIX = {
    'mexc': {'maker': 0.0, 'taker': 0.001} 
}
