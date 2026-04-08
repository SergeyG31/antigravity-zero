import asyncio
import pandas as pd
from core_aggregator import P2PExchangeAggregator
from config import ASSET_PAIR

class P2PMarketScanner:
    def __init__(self, aggregator: P2PExchangeAggregator):
        self.aggregator = aggregator
        self.market_data = {}

    async def fetch_p2p_price_matrix(self):
        """Asynchronously scrapes USDT/ILS P2P prices from 4 exchanges."""
        tasks = []
        # Note: True P2P prices often require specific API calls or scraping in some exchanges.
        # This implementation uses the CCXT Pro order book fetching as a placeholder for low-latency.
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
            # Note: CCXT fetch_order_book is often for spot. Some platforms use the same for P2P if configured.
            # Here we simulate the P2P scan for the dashboard.
            book = await exchange.fetch_order_book(ASSET_PAIR)
            
            # Position #1 Calculation (Top of the book)
            best_bid = book['bids'][0][0] if book['bids'] else 0.0
            best_ask = book['asks'][0][0] if book['asks'] else 0.0
            
            return {
                'name': name,
                'bid': best_bid,
                'ask': best_ask,
                'volume': sum([b[1] for b in book['bids'][:5]]) # Total Liquidity top 5
            }
        except Exception as e:
            print(f"[{name}] Scan Failure: {e}")
            return None

    def calculate_cross_arbitrage(self, fixed_gas_fee=1.0):
        """Identifies gaps between exchanges (Buy on A, Sell on B) accounting for fees."""
        if not self.market_data: return pd.DataFrame()
        
        exchanges = list(self.market_data.keys())
        results = []
        
        for buy_ex in exchanges:
            buy_price = self.market_data[buy_ex]['ask']
            for sell_ex in exchanges:
                if buy_ex == sell_ex: continue
                sell_price = self.market_data[sell_ex]['bid']
                
                if buy_price > 0 and sell_price > 0:
                    # Fee Calculation
                    fee_rate = 0.001 if sell_ex == 'binance' else 0.0  # Simplified fee lookup
                    
                    # Net Profit = (Sell Price * (1 - fee)) - Buy Price - (Gas Fee in ILS / USDT)
                    # For 2500 USDT volume (Standard)
                    volume = 2500.0
                    total_cost = (buy_price * volume) + (fixed_gas_fee * buy_price)
                    total_revenue = (sell_price * volume * (1 - fee_rate))
                    
                    net_profit_pct = (total_revenue - total_cost) / total_cost
                    
                    results.append({
                        'Buy From': buy_ex.upper(),
                        'Sell To': sell_ex.upper(),
                        'Net Spread %': round(net_profit_pct * 100, 2),
                        'Profit (ILS)': round(total_revenue - total_cost, 2),
                        'Status': '🔥 PROFIT' if net_profit_pct > 0.008 else 'HOLD'
                    })
        
        return pd.DataFrame(results).sort_values(by='Net Spread %', ascending=False)

if __name__ == "__main__":
    # Test Run
    async def test_scan():
        agg = P2PExchangeAggregator()
        scanner = P2PMarketScanner(agg)
        print("Scanning Multi-Exchange Market Depth...")
        await scanner.fetch_p2p_price_matrix()
        arb = scanner.calculate_cross_arbitrage()
        print(arb)
    
    asyncio.run(test_scan())
