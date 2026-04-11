import asyncio
import pandas as pd
import time
from auth_manager import AuthManager
from config import CRYPTO_PAIRS, EXCHANGES, TIMEFRAME

class ScraperEngine:
    def __init__(self, auth_mgr: AuthManager):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()
        # price_hub stores full OHLCV dataframes for each symbol
        # format: {symbol: {exchange: pandas_df}}
        self.price_hub = {symbol: {ex: pd.DataFrame() for ex in EXCHANGES} for symbol in (CRYPTO_PAIRS + ['BTC/USDT'])}

    async def scan_ohlcv(self, exchange_id, symbol):
        """Fetches last 50 candles (1m) to calculate indicators."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return pd.DataFrame()
        try:
            # Fetch for strategic indicators
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception:
            return pd.DataFrame()

    async def refresh_all_prices(self):
        """Strategic Scraper: Fetches candle data for all pairs."""
        all_symbols = list(set(CRYPTO_PAIRS + ['BTC/USDT']))
        
        tasks = [self.scan_ohlcv(ex, symbol) for symbol in all_symbols for ex in EXCHANGES]
        results = await asyncio.gather(*tasks)

        idx = 0
        for symbol in all_symbols:
            for ex in EXCHANGES:
                self.price_hub[symbol][ex] = results[idx]
                idx += 1

        return self.price_hub

    def get_latest_price(self, symbol, exchange_id):
        """Helper to get only the last close price."""
        df = self.price_hub.get(symbol, {}).get(exchange_id, pd.DataFrame())
        if not df.empty:
            return df['close'].iloc[-1]
        return 0.0

    def calculate_spread_matrix(self):
        """Compatibility method for dashboard UI."""
        matrix = []
        for symbol, exs in self.price_hub.items():
            for ex_name, df in exs.items():
                if df.empty: continue
                last = df.iloc[-1]
                matrix.append({
                    "Symbol": symbol,
                    "Exchange": ex_name.upper(),
                    "Bid (Buy)": last['close'], # Proxied for UI
                    "Ask (Sell)": last['close'],
                    "Spread %": 0.0
                })
        return pd.DataFrame(matrix)
