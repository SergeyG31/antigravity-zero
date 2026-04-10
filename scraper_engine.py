import asyncio
import pandas as pd
import time
from auth_manager import AuthManager
from config import CRYPTO_PAIRS, EXCHANGES

class ScraperEngine:
    def __init__(self, auth_mgr: AuthManager):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()
        # price_hub structure: {symbol: {exchange: {'buy': bid, 'sell': ask}}}
        self.price_hub = {symbol: {ex: {'buy': 0.0, 'sell': 0.0} for ex in EXCHANGES} for symbol in CRYPTO_PAIRS}

    async def scan_market(self, exchange_id, symbol):
        """Fetches live spot order book for a specific symbol."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange: return 0.0, 0.0
        
        try:
            # High speed fetch
            orderbook = await exchange.fetch_order_book(symbol, 5)
            bid = orderbook['bids'][0][0] if orderbook['bids'] else 0.0
            ask = orderbook['asks'][0][0] if orderbook['asks'] else 0.0
            return bid, ask
        except Exception:
            return 0.0, 0.0

    async def refresh_all_prices(self):
        """Monitors Crypto prices across Binance and MEXC."""
        tasks = []
        for symbol in CRYPTO_PAIRS:
            for ex in EXCHANGES:
                tasks.append(self.wrap_scan(ex, symbol))
        
        results = await asyncio.gather(*tasks)
        
        # Process results into hub
        idx = 0
        for symbol in CRYPTO_PAIRS:
            for ex in EXCHANGES:
                self.price_hub[symbol][ex]['buy'] = results[idx][0]
                self.price_hub[symbol][ex]['sell'] = results[idx][1]
                idx += 1
        
        return self.price_hub


    async def wrap_scan(self, ex, symbol):
        return await self.scan_market(ex, symbol)

    def calculate_spread_matrix(self):
        """Builds a comparison matrix for the dashboard UI."""
        if not self.price_hub: return pd.DataFrame()
        
        matrix = []
        for symbol, exs in self.price_hub.items():
            for ex_name, prices in exs.items():
                matrix.append({
                    "Symbol": symbol,
                    "Exchange": ex_name.upper(),
                    "Bid (Buy)": prices['buy'],
                    "Ask (Sell)": prices['sell'],
                    "Spread %": round(((prices['sell'] - prices['buy']) / prices['buy'] * 100), 2) if prices['buy'] > 0 else 0
                })
        return pd.DataFrame(matrix)

