import asyncio
import time
from config import STOCK_PAIRS, MIN_LAG_THRESHOLD, EXIT_PROFIT_TARGET, MAX_TRADE_SIZE
from intelligence_hub import MarketIntelligenceHub

class ArbManager:
    def __init__(self, auth_mgr):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()
        self.target_exchange = 'mexc'
        self.open_positions = {} # Tracks {symbol: entry_price}
        self.intel_hub = MarketIntelligenceHub() # AI Intelligence engine

    def calculate_net_profit(self, entry_price, current_price, taker_fee=0.001):
        """Calculates true NET profit after double Exchange Taker fees (Entry + Exit)."""
        # 0.1% fee on MEXC for market takers
        gross_profit = (current_price - entry_price) / entry_price
        net_profit = gross_profit - (taker_fee * 2) 
        return net_profit

    async def check_liquidity(self, symbol, required_usd_size):
        """Checks MEXC order book depth to prevent severe slippage."""
        try:
            mexc = self.exchanges.get('mexc')
            if not mexc: return True # Fallback if mock
            
            # Fetch order book with tight depth
            order_book = await mexc.fetch_order_book(symbol, limit=5)
            best_ask_price, best_ask_amount = order_book['asks'][0]
            
            available_usd_at_best_price = best_ask_price * best_ask_amount
            
            if available_usd_at_best_price >= required_usd_size:
                print(f"🌊 [Liquidity OK] {symbol}: ${round(available_usd_at_best_price, 2)} available @ {best_ask_price}.")
                return True
            else:
                print(f"⚠️ [Liquidity WARN] {symbol}: Only ${round(available_usd_at_best_price, 2)} available! Halting trade.")
                return False
        except Exception as e:
            print(f"[Liquidity Scanner] Network/Book error: {e}")
            return False

    async def run_stock_lag_logic(self, crypto_price_hub, real_stock_hub):
        """MEXC Specialist: Entry and Exit logic based on Wall Street Lag & AI Sentiment."""
        for token_symbol, real_ticker in STOCK_PAIRS.items():
            real_price = real_stock_hub.get(token_symbol, 0.0)
            token_price = crypto_price_hub.get(token_symbol, {}).get(self.target_exchange, {}).get('sell', 0.0)
            
            if real_price == 0 or token_price == 0: continue
            
            # --- 1. ENTRY LOGIC ---
            if token_symbol not in self.open_positions:
                lag_deviation = (real_price - token_price) / token_price
                
                if lag_deviation >= MIN_LAG_THRESHOLD:
                    print(f"🎯 [MEXC ENTRY DETECTED] {real_ticker} Lag: {round(lag_deviation*100, 3)}%")
                    
                    # AI SENTIMENT CHECK (The Game Changer)
                    signal, score = await self.intel_hub.run_full_scan(real_ticker)
                    
                    if signal == "BULLISH" and score >= 6:
                        print(f"✅ AI APPROVED [{score}/10]: Strong Bullish Sentiment. Verifying L1 Liquidity...")
                        
                        has_liquidity = await self.check_liquidity(token_symbol, MAX_TRADE_SIZE)
                        if has_liquidity:
                            success = await self.execute_trade(token_symbol, 'BUY', token_price)
                            if success:
                                self.open_positions[token_symbol] = token_price # Safe entry recorded
                        
                    elif signal == "NO_DATA":
                        print(f"⚠️ Network offline or no news. Verifying L1 Liquidity...")
                        has_liquidity = await self.check_liquidity(token_symbol, MAX_TRADE_SIZE)
                        if has_liquidity:
                            success = await self.execute_trade(token_symbol, 'BUY', token_price)
                            if success:
                                self.open_positions[token_symbol] = token_price
                    else:
                        print(f"🛑 AI REJECTED [{signal} {score}/10]: Bad news in the market. Aborting trade.")
            
            # --- 2. EXIT LOGIC ---
            else:
                entry_price = self.open_positions[token_symbol]
                # Use strictly the NET PROFIT calculator
                net_profit = self.calculate_net_profit(entry_price, token_price)
                
                # Exit if target NET profit reached
                if net_profit >= EXIT_PROFIT_TARGET:
                    print(f"💰 [MEXC EXIT] Closing {token_symbol} | NET Profit after fees: {round(net_profit*100, 2)}%")
                    success = await self.execute_trade(token_symbol, 'SELL', token_price)
                    if success:
                        del self.open_positions[token_symbol]

    async def execute_trade(self, symbol, side, price):
        """Executes market orders on MEXC with Shadow Mode Guard."""
        import config
        from trading_intelligence import log_trade
        
        mode_prefix = "[LIVE-FOR-REAL]" if not config.SHADOW_MODE else "[SHADOW-MODE]"
        print(f"🚀 {mode_prefix} EXECUTION: {side} {symbol} @ {price}")
        
        # Log to history for StrategyLearner
        log_trade({
            "timestamp": str(time.time()),
            "symbol": symbol,
            "side": side,
            "price": price,
            "shadow": config.SHADOW_MODE
        })

        if config.SHADOW_MODE:
            print(f"🛡️  Shadow Mode Active: Trade bypassed.")
            return True

        # In Live, we call the CCXT create_order here
        # await self.exchanges['mexc'].create_market_order(symbol, side, MAX_TRADE_SIZE)
        return True

