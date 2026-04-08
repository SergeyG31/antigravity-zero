import ccxt
from config import EXCHANGES, SAFETY_OFFSET, AGGRESSIVE_MODE, MIN_SPREAD_GAP

class AdCommander:
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'bybit': ccxt.bybit(),
            'okx': ccxt.okx(),
            'mexc': ccxt.mexc(),
        }

    def update_ad_aggression(self, exchange_id, ad_id, target_price):
        """Aggressive Price War Strategy: under-cut by $0.001 ILS."""
        # Calculate Competition (Top 3 competitors)
        # Undercut competitor
        current_ad_price = target_price - SAFETY_OFFSET
        
        # Security: Check if we are still above the min spread
        if current_ad_price < 3.60: # Threshold for profitability
            print(f"[{exchange_id}] Profit boundary hit. Stopping under-cut on Ad {ad_id}.")
            return False

        if AGGRESSIVE_MODE:
            print(f"[{exchange_id}] Under-cutting competitors on Ad {ad_id} to {current_ad_price} ILS")
            # In a real scenario, this would call the exchange API to update the P2P ad.
            # await self.exchanges[exchange_id].private_post_update_p2p_ad({'ad_id': ad_id, 'price': current_ad_price})
            return True
        return False
