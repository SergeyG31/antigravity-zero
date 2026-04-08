import ccxt.pro as ccxt
import os
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    def __init__(self):
        self.exchanges = {}
        self.init_exchanges()

    def init_exchanges(self):
        """Initializes all 4 hubs for P2P trading using CCXT Pro."""
        # Binance
        self.exchanges['binance'] = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY', ''),
            'secret': os.getenv('BINANCE_API_SECRET', ''),
            'enableRateLimit': True,
        })

        # Bybit
        self.exchanges['bybit'] = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_API_KEY', ''),
            'secret': os.getenv('BYBIT_API_SECRET', ''),
            'enableRateLimit': True,
        })

        # OKX
        self.exchanges['okx'] = ccxt.okx({
            'apiKey': os.getenv('OKX_API_KEY', ''),
            'secret': os.getenv('OKX_API_SECRET', ''),
            'password': os.getenv('OKX_PASSPHRASE', ''),
            'enableRateLimit': True,
        })

        # MEXC
        self.exchanges['mexc'] = ccxt.mexc({
            'apiKey': os.getenv('MEXC_API_KEY', ''),
            'secret': os.getenv('MEXC_API_SECRET', ''),
            'enableRateLimit': True,
        })

        # Bitget
        self.exchanges['bitget'] = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY', ''),
            'secret': os.getenv('BITGET_API_SECRET', ''),
            'password': os.getenv('BITGET_PASSWORD', ''),
            'enableRateLimit': True,
        })

    def get_exchange(self, exchange_id):
        return self.exchanges.get(exchange_id)

    def get_all_exchanges(self):
        return self.exchanges
