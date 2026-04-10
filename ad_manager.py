import asyncio
import time
import json
import os
from config import CRYPTO_PAIRS, MOMENTUM_THRESHOLD, EXIT_PROFIT_TARGET, MAX_TRADE_SIZE, TARGET_EXCHANGE, MEXC_TAKER_FEE
from intelligence_hub import MarketIntelligenceHub

class ArbManager:
    def __init__(self, auth_mgr):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()
        self.positions_file = 'active_positions.json'
        self.open_positions = self.load_positions() 
        self.price_history = {}    
        self.intel_hub = MarketIntelligenceHub()

    def load_positions(self):
        """Loads open trades from disk to handle restarts."""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_positions(self):
        """Saves current open trades to disk."""
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(self.open_positions, f)
        except Exception as e:
            print(f"❌ Failed to save positions: {e}")


    def calculate_net_profit(self, entry_price, current_price):
        """Calculates true NET profit after double Exchange Taker fees."""
        gross_profit = (current_price - entry_price) / entry_price
        net_profit = gross_profit - (MEXC_TAKER_FEE * 2) 
        return net_profit

    async def check_liquidity(self, symbol, required_usd_size):
        """Checks MEXC order book depth."""
        try:
            mexc = self.exchanges.get(TARGET_EXCHANGE)
            order_book = await mexc.fetch_order_book(symbol, limit=5)
            best_ask_price, best_ask_amount = order_book['asks'][0]
            if (best_ask_price * best_ask_amount) >= required_usd_size:
                return True
            return False
        except Exception:
            return False

    async def run_crypto_smart_logic(self, price_hub):
        """Smart Crypto (MEXC ONLY): Momentum + Sentiment Logic."""
        from config import MAX_CONCURRENT_TRADES, MIN_AI_SCORE
        
        for symbol in CRYPTO_PAIRS:
            current_price = price_hub.get(symbol, {}).get(TARGET_EXCHANGE, {}).get('sell', 0.0)
            if current_price == 0: continue
            
            # --- 1. ENTRY LOGIC: Momentum + AI Confidence ---
            if symbol not in self.open_positions:
                if len(self.open_positions) >= MAX_CONCURRENT_TRADES: continue
                
                prev_price = self.price_history.get(symbol, 0.0)
                self.price_history[symbol] = current_price # Update history
                
                if prev_price > 0:
                    momentum = (current_price - prev_price) / prev_price
                    
                    # If price is moving up, verify with AI
                    if momentum >= MOMENTUM_THRESHOLD:
                        print(f"📈 [HYPER] {symbol} Up {round(momentum*100, 3)}%. Verifying...")
                        
                        base_ticker = symbol.split('/')[0]
                        signal, score = await self.intel_hub.run_full_scan(base_ticker)
                        
                        # LOG THE RESULT ALWAYS (So the user knows why it didn't buy)
                        print(f"🤖 [AI DECISION] {symbol}: Signal={signal}, Score={score}/10")
                        
                        if signal == "BULLISH" and score >= MIN_AI_SCORE:
                            if await self.check_liquidity(symbol, MAX_TRADE_SIZE):
                                success = await self.execute_trade(symbol, 'BUY', current_price)
                                if success:
                                    self.open_positions[symbol] = current_price
                                    self.save_positions()
                        elif signal == "NO_DATA" and momentum >= (MOMENTUM_THRESHOLD * 3):
                            # Special case: If news API is down but momentum is HUGE (3x threshold), enter anyway
                            print(f"⚡ [MOMENTUM FALLBACK] No news data, but price jump is massive! Entering...")
                            if await self.check_liquidity(symbol, MAX_TRADE_SIZE):
                                success = await self.execute_trade(symbol, 'BUY', current_price)
                                if success:
                                    self.open_positions[symbol] = current_price
                                    self.save_positions()
                        else:
                            print(f"⏳ [STANDBY] {symbol} rejected by AI or Score too low.")
            
            # --- 2. EXIT LOGIC ---
            else:
                entry_price = self.open_positions[symbol]
                current_bid = price_hub.get(symbol, {}).get(TARGET_EXCHANGE, {}).get('buy', 0.0)
                if current_bid == 0: continue
                
                net_profit = self.calculate_net_profit(entry_price, current_bid)
                
                if net_profit >= EXIT_PROFIT_TARGET:
                    print(f"💰 [MEXC PROFIT] Closing {symbol} | Net: {round(net_profit*100, 2)}%")
                    success = await self.execute_trade(symbol, 'SELL', current_bid)
                    if success:
                        del self.open_positions[symbol]
                        self.save_positions() # Persist to disk

    async def execute_trade(self, symbol, side, price):
        """Executes market orders on MEXC with Shadow Mode Guard and Telegram Alert."""
        import config
        from trading_intelligence import log_trade
        from telegram_notifier import TelegramNotifier
        
        notifier = TelegramNotifier()
        mode_prefix = "[LIVE-FOR-REAL]" if not config.SHADOW_MODE else "[SHADOW-MODE]"
        msg = f"🚀 {mode_prefix} EXECUTION: {side} {symbol} @ {price}"
        print(msg)
        
        # Log to history for StrategyLearner
        log_trade({
            "timestamp": str(time.time()),
            "symbol": symbol,
            "side": side,
            "price": price,
            "shadow": config.SHADOW_MODE
        })

        # Send Telegram Notification for Execution
        notifier.send_message(msg)

        if config.SHADOW_MODE:
            print(f"🛡️  Shadow Mode Active: Trade bypassed.")
            return True

        # In Live, we call the CCXT create_order here
        try:
            mexc = self.exchanges['mexc']
            # Calculate how many tokens we get for $10
            token_amount = config.MAX_TRADE_SIZE / price
            
            # Ensure the amount is not too small (below 1 USDT volume)
            if (token_amount * price) < 1.0:
                print(f"⚠️ Trade volume too small: {token_amount * price} USDT. Skipping.")
                return False

            if side.upper() == 'BUY':
                print(f"💰 Executing Live BUY: {token_amount} {symbol} (Cost: ${config.MAX_TRADE_SIZE})")
                # CCXT MEXC market buy expects the AMOUNT of tokens, not the cost.
                await mexc.create_market_buy_order(symbol, token_amount)
            else:
                print(f"💰 Executing Live SELL: {token_amount} {symbol} @ {price}")
                await mexc.create_market_sell_order(symbol, token_amount)
                
            return True
        except Exception as e:
            error_msg = str(e).replace('_', ' ').replace('*', ' ') # Clean for Telegram
            print(f"❌ EXECUTION FAILED: {error_msg}")
            notifier.send_message(f"❌ *TRADE FAILURE*: {symbol} {side}\n{error_msg}")
            return False

# Alias for compatibility with dashboard_hud.py
AdManager = ArbManager


