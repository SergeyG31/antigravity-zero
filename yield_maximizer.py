import pandas as pd
from config import EXCHANGES, FEE_MATRIX, FIXED_GAS_FEE, CROSS_EXCHANGE_THRESHOLD

class YieldMaximizer:
    def __init__(self, scraper):
        self.scraper = scraper 

    def get_best_arbitrage_opportunity(self, total_balance=0.0):
        """Analyzes all pairs to find the highest NET profit opportunity."""
        # Growth Guard: If balance is low, avoid cross-exchange suggestions
        if total_balance < CROSS_EXCHANGE_THRESHOLD:
            return pd.DataFrame() # Return empty if below threshold
        
        prices = self.scraper.price_hub
        opportunities = []

        # Compare Buying on Exchange A vs Selling on Exchange B
        for buy_ex in EXCHANGES:
            # We BUY from someone selling USDT - we look at their SELL price
            # or if we are a maker, our ASK price to buy.
            # Simplified: buy_from_price = price to acquire USDT
            buy_price = prices.get(buy_ex, {}).get('buy', 0.0)
            
            for sell_ex in EXCHANGES:
                if buy_ex == sell_ex: continue
                
                sell_price = prices.get(sell_ex, {}).get('sell', 0.0)
                
                if buy_price > 0 and sell_price > 0:
                    # Fee Calculation:
                    # 1. Exchange fees (Maker on both sides if we post ads)
                    buy_fee = FEE_MATRIX.get(buy_ex, {'maker': 0.0})['maker']
                    sell_fee = FEE_MATRIX.get(sell_ex, {'maker': 0.0})['maker']
                    
                    # 2. Transfer cost (Gas)
                    # For a 1000 USDT trade example:
                    volume_usdt = 1000.0
                    total_buy_cost_ils = (buy_price * volume_usdt) * (1 + buy_fee)
                    
                    # After buy, we transfer. Volume becomes volume - gas_fee
                    transferable_usdt = volume_usdt - FIXED_GAS_FEE
                    
                    total_sell_rev_ils = (sell_price * transferable_usdt) * (1 - sell_fee)
                    
                    net_profit_ils = total_sell_rev_ils - total_buy_cost_ils
                    roi_pct = (net_profit_ils / total_buy_cost_ils) * 100

                    if roi_pct > 0:
                        opportunities.append({
                            'Pair': f"{buy_ex.upper()} ➔ {sell_ex.upper()}",
                            'Buy Price': buy_price,
                            'Sell Price': sell_price,
                            'Net Profit (₪)': round(net_profit_ils, 2),
                            'ROI (%)': round(roi_pct, 2)
                        })

        # Sort by best ROI
        df = pd.DataFrame(opportunities)
        if not df.empty:
            return df.sort_values(by='ROI (%)', ascending=False)
        return pd.DataFrame()

if __name__ == "__main__":
    # Internal test with mock data
    class MockScraper:
        price_hub = {
            'mexc': {'buy': 3.60, 'sell': 3.62},
            'binance': {'buy': 3.68, 'sell': 3.70},
            'bybit': {'buy': 3.65, 'sell': 3.67},
            'okx': {'buy': 3.66, 'sell': 3.68},
            'bitget': {'buy': 3.64, 'sell': 3.66}
        }
    
    maximizer = YieldMaximizer(MockScraper())
    print("Finding best P2P Arbitrage opportunities...")
    best = maximizer.get_best_arbitrage_opportunity()
    print(best)
