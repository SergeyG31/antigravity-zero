import asyncio
import time
import json
import os
import pandas as pd
from config import (
    CRYPTO_PAIRS, MOMENTUM_THRESHOLD, EXIT_PROFIT_TARGET, MAX_TRADE_SIZE,
    TARGET_EXCHANGE, MEXC_TAKER_FEE, MAX_CONCURRENT_TRADES, MIN_AI_SCORE,
    STOP_LOSS_LIMIT, VOLUME_MA_THRESHOLD, BTC_MOMENTUM_LIMIT,
    RSI_BUY_THRESHOLD, RSI_SELL_THRESHOLD, BOLLINGER_WINDOW, BOLLINGER_STD
)
from intelligence_hub import MarketIntelligenceHub

class ArbManager:
    def __init__(self, auth_mgr):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()
        self.positions_file = 'active_positions.json'
        self.open_positions = self.load_positions() 
        self.btc_history = []      # list of [timestamp, price]
        self.intel_hub = MarketIntelligenceHub()

    def get_btc_safe_status(self, current_btc_price):
        """Task 2: Monitor BTC/USDT price change in a 30-second rolling window."""
        now = time.time()
        self.btc_history.append([now, current_btc_price])
        self.btc_history = [x for x in self.btc_history if now - x[0] <= 35]
        if len(self.btc_history) < 2: return True
        oldest_btc = self.btc_history[0][1]
        btc_change = (current_btc_price - oldest_btc) / oldest_btc
        if btc_change <= BTC_MOMENTUM_LIMIT:
            print(f"⚠️ [GLOBAL PAUSE] BTC dropped {round(btc_change*100, 3)}% in 30s. Market unsafe.")
            return False
        return True

    def calculate_indicators(self, df):
        """Strategic Indicator Engine: RSI + Bollinger Bands."""
        if len(df) < BOLLINGER_WINDOW:
            return None
        
        # 1. Bollinger Bands
        df['sma'] = df['close'].rolling(window=BOLLINGER_WINDOW).mean()
        df['std'] = df['close'].rolling(window=BOLLINGER_WINDOW).std()
        df['upper'] = df['sma'] + (df['std'] * BOLLINGER_STD)
        df['lower'] = df['sma'] - (df['std'] * BOLLINGER_STD)
        
        # 2. RSI (14 periods)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df.iloc[-1]

    async def run_crypto_smart_logic(self, price_hub):
        """Strategic Value Hunter: Hunt for Support/Resistance patterns."""
        btc_price = 0.0
        btc_df = price_hub.get('BTC/USDT', {}).get(TARGET_EXCHANGE, pd.DataFrame())
        if not btc_df.empty:
            btc_price = btc_df['close'].iloc[-1]
        
        market_is_safe = self.get_btc_safe_status(btc_price) if btc_price > 0 else True

        for symbol in CRYPTO_PAIRS:
            df = price_hub.get(symbol, {}).get(TARGET_EXCHANGE, pd.DataFrame())
            if df.empty: continue
            
            latest = self.calculate_indicators(df)
            if latest is None: continue
            
            current_price = latest['close']
            current_rsi = latest['rsi']
            lower_band = latest['lower']
            upper_band = latest['upper']
            sma = latest['sma']
            
            # --- 1. ENTRY LOGIC: Support Hunter ---
            if symbol not in self.open_positions:
                if not market_is_safe: continue
                if len(self.open_positions) >= MAX_CONCURRENT_TRADES: continue
                
                # Condition: Price at Support AND Oversold
                is_cheap = (current_price <= lower_band) and (current_rsi <= RSI_BUY_THRESHOLD)
                
                if is_cheap:
                    print(f"🎯 [STRATEGIC BUY] {symbol} | Price: {current_price} (<= {round(lower_band, 5)}) | RSI: {round(current_rsi, 1)}")
                    
                    try:
                        ai_task = asyncio.create_task(self.intel_hub.run_full_scan(symbol.split('/')[0]))
                        signal, score = await asyncio.wait_for(ai_task, timeout=1.5)
                    except Exception:
                        # Value Override: proceed if support is very strong
                        print(f"🚀 [VALUE OVERRIDE] Technical indicators are very strong. Proceeding without AI.")
                        signal, score = "BULLISH", 10
                    
                    if signal == "BULLISH" and score >= MIN_AI_SCORE:
                        success = await self.execute_trade(symbol, 'BUY', current_price)
                        if success:
                            self.open_positions[symbol] = current_price
                            self.save_positions()
                            
            # --- 2. EXIT LOGIC: Resistance Hunter ---
            else:
                entry_price = self.open_positions[symbol]
                if not isinstance(entry_price, (int, float)): continue
                
                net_profit = self.calculate_net_profit(entry_price, current_price)
                veto_key = f"{symbol}_veto"
                
                # A. EMERGENCY: SL or AI VETO
                if net_profit <= STOP_LOSS_LIMIT or veto_key in self.open_positions:
                    reason = "STOP LOSS" if net_profit <= STOP_LOSS_LIMIT else "AI VETO"
                    print(f"🚨 [{reason}] Closing {symbol} (PnL: {round(net_profit*100, 2)}%).")
                    success = await self.execute_trade(symbol, 'SELL', current_price)
                    if success:
                        del self.open_positions[symbol]
                        if veto_key in self.open_positions: del self.open_positions[veto_key]
                        self.save_positions()
                    continue

                # B. STRATEGIC EXIT: Price touched Upper Band (Overbought)
                is_expensive = (current_price >= upper_band) or (current_rsi >= RSI_SELL_THRESHOLD)
                
                if is_expensive and net_profit >= EXIT_PROFIT_TARGET:
                    print(f"💰 [STRATEGIC EXIT] {symbol} (PnL: {round(net_profit*100, 2)}%) | Price: {current_price} >= {round(upper_band, 5)}")
                    success = await self.execute_trade(symbol, 'SELL', current_price)
                    if success:
                        del self.open_positions[symbol]
                        peak_key = f"{symbol}_peak"
                        if peak_key in self.open_positions: del self.open_positions[peak_key]
                        self.save_positions()
                
                # C. TRAILING EXIT (Optional backup)
                elif net_profit >= EXIT_PROFIT_TARGET:
                    peak_key = f"{symbol}_peak"
                    if peak_key not in self.open_positions:
                        self.open_positions[peak_key] = current_price
                    peak_price = max(self.open_positions[peak_key], current_price)
                    self.open_positions[peak_key] = peak_price
                    if (peak_price - current_price) / peak_price >= 0.0005: 
                        print(f"🌊 [TRAILING EXIT] {symbol} (PnL: {round(net_profit*100, 2)}%)")
                        success = await self.execute_trade(symbol, 'SELL', current_price)
                        if success:
                            del self.open_positions[symbol]
                            if peak_key in self.open_positions: del self.open_positions[peak_key]
                            self.save_positions()

    def calculate_net_profit(self, entry_price, current_price):
        """Calculates true NET profit after double Exchange Taker fees."""
        gross_profit = (current_price - entry_price) / entry_price
        net_profit = gross_profit - (MEXC_TAKER_FEE * 2) 
        return net_profit

    def formalize_amount(self, symbol, amount):
        """Normalizes amount to exchange precision specs."""
        mexc = self.exchanges['mexc']
        return float(mexc.amount_to_precision(symbol, amount))

    async def execute_trade(self, symbol, side, price):
        """Executes market orders on MEXC."""
        import config
        from telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier()
        mode_prefix = "[LIVE-FOR-REAL]" if not config.SHADOW_MODE else "[SHADOW-MODE]"
        msg = f"🚀 {mode_prefix} EXECUTION: {side} {symbol} @ {price}"
        print(msg)
        notifier.send_message(msg)

        if config.SHADOW_MODE: return True

        try:
            mexc = self.exchanges['mexc']
            if side.upper() == 'SELL':
                base_asset = symbol.split('/')[0]
                balance = await mexc.fetch_balance()
                actual_amount = balance['total'].get(base_asset, 0)
                if actual_amount > 0:
                    token_amount = self.formalize_amount(symbol, actual_amount)
                    await mexc.create_market_sell_order(symbol, token_amount)
                    return True
                return False
            
            token_amount = self.formalize_amount(symbol, config.MAX_TRADE_SIZE / price)
            await mexc.create_market_buy_order(symbol, token_amount)
            return True
        except Exception as e:
            print(f"❌ EXECUTION FAILED: {e}")
            return False

    def load_positions(self):
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            except Exception: return {}
        return {}

    def save_positions(self):
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(self.open_positions, f)
        except Exception as e: print(f"❌ Failed to save positions: {e}")

AdManager = ArbManager
