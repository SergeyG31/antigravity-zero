import asyncio
import pandas as pd
from core_aggregator import P2PExchangeAggregator
from config import ASSET_PAIR

class MultiMarketScanner:
    def __init__(self, aggregator=None):
        from core_aggregator import P2PExchangeAggregator
        self.aggregator = aggregator or P2PExchangeAggregator()
        self.market_data = {}

    async def scan_all_depths(self):
        """Asynchronously scans depths across all exchanges."""
        tasks = []
        for name, exchange in self.aggregator.exchanges.items():
            tasks.append(self.fetch_single_depth(name, exchange))
        
        results = await asyncio.gather(*tasks)
        for res in results:
            if res:
                self.market_data[res['name']] = res
        
        return self.market_data

    async def fetch_single_depth(self, name, exchange):
        """Scans the depth of a specific market for Position #1 estimation."""
        try:
            # Note: CCXT fetch_order_book is often for spot.
            book = await exchange.fetch_order_book(ASSET_PAIR)
            
            # Position #1 Calculation (Top of the book)
            best_bid = book['bids'][0][0] if book['bids'] else 0.0
            best_ask = book['asks'][0][0] if book['asks'] else 0.0
            
            return {
                'name': name,
                'bid': best_bid,
                'ask': best_ask,
                'volume': sum([b[1] for b in book['bids'][:5]]) 
            }
        except Exception as e:
            print(f"[{name}] Scan Failure: {e}")
            return {'name': name, 'bid': 0.0, 'ask': 0.0, 'volume': 0.0}

    def find_cross_arb(self, depths=None):
        """Finds arbitrage opportunities in the provided depths."""
        data = depths or self.market_data
        if not data: return None
        
        best_opp = None
        max_spread = -1.0
        
        exchanges = list(data.keys())
        for buy_ex in exchanges:
            buy_price = data[buy_ex]['ask']
            if buy_price <= 0: continue
            
            for sell_ex in exchanges:
                if buy_ex == sell_ex: continue
                sell_price = data[sell_ex]['bid']
                if sell_price <= 0: continue
                
                spread = (sell_price - buy_price) / buy_price
                if spread > max_spread:
                    max_spread = spread
                    best_opp = f"Buy {buy_ex.upper()} @ {buy_price} -> Sell {sell_ex.upper()} @ {sell_price} (Spread: {round(spread*100, 2)}%)"
        
        return best_opp if max_spread > 0.005 else None # 0.5% threshold

if __name__ == "__main__":
    # Test Run
    async def test_scan():
        scanner = MultiMarketScanner()
        print("Scanning Multi-Exchange Market Depth...")
        depths = await scanner.scan_all_depths()
        arb = scanner.find_cross_arb(depths)
        print(f"Best Arb: {arb}")
    
    asyncio.run(test_scan())

