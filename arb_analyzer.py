import requests
from config import MIN_SPREAD, USD_ILS_HEDGE_BUFFER

class YieldMaximizer:
    def __init__(self):
        self.bybit_spread = 0.0
        self.okx_spread = 0.0
        self.usd_ils_price = 0.0

    def fetch_forex_data(self):
        """Fetches live USD/ILS market price for hedging."""
        try:
            # Using free Currency API or Alpha Vantage
            resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = resp.json()
            self.usd_ils_price = data['rates']['ILS']
            return self.usd_ils_price
        except Exception as e:
            print(f"Forex fetch error: {e}")
            return 3.65  # Hardcoded cautious fallback if API is down

    def analyze_spreads(self, bybit_orderbook, okx_orderbook):
        """Cross-platform Arbitrage: calculates best yield."""
        # Calculate Bybit Spread %
        self.bybit_spread = (bybit_orderbook['asks'][0][0] - bybit_orderbook['bids'][0][0]) / bybit_orderbook['bids'][0][0]
        # Calculate OKX Spread %
        self.okx_spread = (okx_orderbook['asks'][0][0] - okx_orderbook['bids'][0][0]) / okx_orderbook['bids'][0][0]

        # Decision: If Bybit spread is too low, shift liquidity to OKX
        if self.bybit_spread < MIN_SPREAD:
            return "OKX" # Shift focused liquidity to OKX
        elif self.okx_spread < MIN_SPREAD:
            return "BYBIT"
        else:
            return "BOTH"

    def apply_hedging(self, current_sell_price):
        """Forex Hedging: adjust sell price if USD is crashing."""
        # If USD drops, our ILS value drops. We raise the ILS sell price to protect USD equivalent.
        forex_rate = self.fetch_forex_data()
        
        # Example logic: if USD/ILS drops by more than buffer, raise sell price by 0.5%
        if forex_rate < 3.60: # Threshold for USD crash
            new_price = current_sell_price * (1 + 0.005)
            print(f"Forex Hedge: USD/ILS is low ({forex_rate}). Raising Sell: {new_price}")
            return new_price
        return current_sell_price
