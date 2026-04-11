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
    def formalize_amount(self, symbol, amount):
        """Normalizes amount to exchange precision specs."""
        mexc = self.exchanges['mexc']
        return float(mexc.amount_to_precision(symbol, amount))

    async def optimistic_ai_verify(self, symbol):
        """Verify the trade with AI after entry. If bad, flag for veto exit."""
        from config import MIN_AI_SCORE
        base_ticker = symbol.split('/')[0]
        signal, score = await self.intel_hub.run_full_scan(base_ticker)
        
        # VETO only if it's truly dangerous (Bearish or VERY low score)
        if signal == "BEARISH" or score < 3:
            print(f"⚠️ [AI VETO] {symbol} confirmed danger (Signal: {signal}, Score: {score}/10). Closing...")
            self.open_positions[f"{symbol}_veto"] = True
        else:
            print(f"✅ [AI PASSED] {symbol} is safe to hold (Signal: {signal}, Score: {score}/10).")
            
    async def liquidate_everything(self):
        """Emergency method to sell all open positions recorded in memory."""
        print("🕯️ Antigravity Ritual: Liquidating all assets...")
        # Get all coin keys (ignoring peak/veto keys)
        symbols = [s for s in self.open_positions.keys() if '/' in s and not s.endswith('_peak') and not s.endswith('_veto')]
        for symbol in symbols:
            # We use 0 as price to trigger market fetch in execute_trade
            await self.execute_trade(symbol, 'SELL', 0)
            if symbol in self.open_positions: del self.open_positions[symbol]
            # Cleanup metadata keys
            for k in [f"{symbol}_peak", f"{symbol}_veto"]:
                if k in self.open_positions: del self.open_positions[k]
        self.save_positions()

    async def run_crypto_smart_logic(self, price_hub):
        """Optimistic Hyper-Aggressive Logic: Buy on Signal, Verify in Background."""
        from config import MAX_CONCURRENT_TRADES, CRYPTO_PAIRS, TARGET_EXCHANGE, MOMENTUM_THRESHOLD
        
        for symbol in CRYPTO_PAIRS:
            current_price = price_hub.get(symbol, {}).get(TARGET_EXCHANGE, {}).get('sell', 0.0)
            if current_price == 0: continue
            
            # --- 1. ENTRY LOGIC: Optimistic Buy ---
            if symbol not in self.open_positions:
                if len(self.open_positions) >= MAX_CONCURRENT_TRADES: continue
                
                prev_price = self.price_history.get(symbol, 0.0)
                self.price_history[symbol] = current_price
                
                if prev_price > 0:
                    momentum = (current_price - prev_price) / prev_price
                    
                    if momentum >= MOMENTUM_THRESHOLD:
                        print(f"🚀 [OPTIMISTIC BUY] {symbol} Up {round(momentum*100, 4)}%. Executing...")
                        success = await self.execute_trade(symbol, 'BUY', current_price)
                        if success:
                            self.open_positions[symbol] = current_price
                            self.save_positions()
                            # Verify in background
                            asyncio.create_task(self.optimistic_ai_verify(symbol))
            
            # --- 2. EXIT LOGIC (Trailing + SL + AI Veto) ---
            else:
                from config import STOP_LOSS_LIMIT, EXIT_PROFIT_TARGET
                entry_data = self.open_positions[symbol]
                # Entry price is just the value
                entry_price = entry_data
                
                current_bid = price_hub.get(symbol, {}).get(TARGET_EXCHANGE, {}).get('buy', 0.0)
                if current_bid == 0: continue
                
                net_profit = self.calculate_net_profit(entry_price, current_bid)
                
                # A. STOP LOSS or AI VETO
                veto_key = f"{symbol}_veto"
                should_emergency_exit = net_profit <= STOP_LOSS_LIMIT or veto_key in self.open_positions
                
                if should_emergency_exit:
                    reason = "STOP LOSS" if net_profit <= STOP_LOSS_LIMIT else "AI VETO"
                    print(f"🚨 [{reason}] Closing {symbol} (PnL: {round(net_profit*100, 2)}%).")
                    success = await self.execute_trade(symbol, 'SELL', current_bid)
                    if success:
                        del self.open_positions[symbol]
                        if veto_key in self.open_positions: del self.open_positions[veto_key]
                        self.save_positions()
                    continue

                # B. TRAILING TAKE PROFIT: Ride the wave
                if net_profit >= EXIT_PROFIT_TARGET:
                    # Store the highest price seen since hitting target
                    peak_key = f"{symbol}_peak"
                    if peak_key not in self.open_positions:
                        self.open_positions[peak_key] = current_bid
                    
                    peak_price = max(self.open_positions[peak_key], current_bid)
                    self.open_positions[peak_key] = peak_price
                    
                    # If price drops 0.05% from the peak, or we just want to lock in 
                    # a very high profit, we sell.
                    drop_from_peak = (peak_price - current_bid) / peak_price
                    
                    if drop_from_peak >= 0.0005: # 0.05% drop from peak
                        print(f"💰 [TAKE PROFIT] {symbol} Peak: {peak_price} | Current: {current_bid} | Net: {round(net_profit*100, 2)}%")
                        success = await self.execute_trade(symbol, 'SELL', current_bid)
                        if success:
                            del self.open_positions[symbol]
                            if peak_key in self.open_positions: del self.open_positions[peak_key]
                            self.save_positions()
                    else:
                        print(f"🌊 [RIDING WAVE] {symbol} at {round(net_profit*100, 2)}%. Peak: {peak_price}. Waiting for higher...")

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
                token_amount = self.formalize_amount(symbol, token_amount)
                print(f"💰 Executing Live BUY: {token_amount} {symbol} (Cost: ${config.MAX_TRADE_SIZE})")
                await mexc.create_market_buy_order(symbol, token_amount)
            else:
                # For SELL: Fetch actual balance to avoid 'Oversold' errors
                base_asset = symbol.split('/')[0]
                balance = await mexc.fetch_balance()
                actual_amount = balance['total'].get(base_asset, 0)
                
                if actual_amount > 0:
                    token_amount = self.formalize_amount(symbol, actual_amount)
                    print(f"💰 Executing Live SELL: {token_amount} {symbol} (Full Balance)")
                    await mexc.create_market_sell_order(symbol, token_amount)
                else:
                    print(f"⚠️ No balance found for {base_asset}. Removing phantom position from memory.")
                    if symbol in self.open_positions:
                        del self.open_positions[symbol]
                        # Also clean up potential peak keys
                        peak_key = f"{symbol}_peak"
                        if peak_key in self.open_positions: del self.open_positions[peak_key]
                        self.save_positions()
                    return False
                
            return True
        except Exception as e:
            error_msg = str(e).replace('_', ' ').replace('*', ' ') # Clean for Telegram
            print(f"❌ EXECUTION FAILED: {error_msg}")
            notifier.send_message(f"❌ *TRADE FAILURE*: {symbol} {side}\n{error_msg}")
            return False

# Alias for compatibility with dashboard_hud.py
AdManager = ArbManager


