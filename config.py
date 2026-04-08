import os
from dotenv import load_dotenv

load_dotenv()

# --- GEMINI AI CONFIG ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# --- MEXC Stock Specialist Mode ---
EXCHANGE_ID = 'mexc' # Primary exchange for Stock Tokens
ASSET_PAIR = 'USDT/ILS' # Used in P2P logic
ASSET_PAIRS = ['BTC/USDT', 'ETH/USDT'] # Disabling standard crypto loops
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
MAX_ORDER_SIZE = 1000.0     # Maximum size for arb orders
MIN_LIQUIDITY_BRAKE = 100.0 # Pause if book depth < $100
FIXED_GAS_FEE = 1.0         # Estimated transfer cost in USDT
CROSS_EXCHANGE_THRESHOLD = 500.0 # Min balance to attempt cross-exchange
SCAN_TIMEOUT = 10           # Frequency of market scans (seconds)

# --- P2P Aggregator Settings ---
SAFETY_OFFSET = 0.001       # Amount to undercut competitors (ILS)
AGGRESSIVE_MODE = True      # Enable aggressive undercutting
MIN_SPREAD_GAP = 0.005      # Minimum spread to maintain (percentage)
SCAN_TIMEOUT = 10           # Frequency of market scans (seconds)
SAFETY_MODE = True          # Enable AI Verification and Safety Checks


# --- API Keys (Stored in .env) ---
MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')

# --- Intelligence & Learning (Strict Additive) ---
SHADOW_MODE = False           # set to False for LIVE execution
INTELLIGENCE_RECON_INTERVAL = 300 # Deep learning scan every 5 minutes
TRADE_HISTORY_FILE = 'trade_history.json'
INSIGHTS_LOG_FILE = 'learning_insights.log'

# Fee settings for MEXC
EXCHANGES = ['binance', 'bybit', 'okx', 'mexc']
FEE_MATRIX = {
    'mexc': {'maker': 0.0, 'taker': 0.001},
    'binance': {'maker': 0.001, 'taker': 0.001},
    'bybit': {'maker': 0.0, 'taker': 0.001},
    'okx': {'maker': 0.0, 'taker': 0.001}
}


