import json
import os
import asyncio
import google.generativeai as genai
from datetime import datetime
import config

class TradingIntelligence:
    class StrategyLearner:
        def __init__(self):
            self.history_file = config.TRADE_HISTORY_FILE
            self.insights_file = config.INSIGHTS_LOG_FILE
            
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                # Using 1.5 Pro for deeper reflective learning as requested
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            else:
                self.model = None

        async def learn_from_history(self):
            """Reflective Learning: Analyzes past trades to extract strategy improvements."""
            if not self.model or not os.path.exists(self.history_file):
                return

            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                
                if not history: return

                print(f"🧠 [StrategyLearner] Analyzing {len(history)} past trades for improvements...")
                
                prompt = f"""
                You are a Strategic Trading Auditor. Review the following trade history:
                {json.dumps(history[-10:])} 
                
                Compare these results with the current market behavior. 
                Identify patterns where the bot was 'Too Aggressive' or 'Too Late'.
                Output 3 actionable bullets for strategy optimization.
                Strict JSON Output: {"insights": ["...", "..."]}
                """
                
                response = self.model.generate_content(prompt)
                insight_data = response.text
                
                with open(self.insights_file, 'a') as log:
                    log.write(f"[{datetime.now()}] REFILCTION: {insight_data}\n")
                
                print("✅ [StrategyLearner] New strategic insights logged.")
                
            except Exception as e:
                print(f"❌ [StrategyLearner] Learning Error: {e}")

    class SentimentMonitor:
        """Encapsulated Sentiment Scanner with Jitter."""
        def __init__(self):
            from intelligence_hub import MarketIntelligenceHub
            self.hub = MarketIntelligenceHub()

        async def background_recon(self):
            """Periodically scans top stocks to warm up the sentiment cache."""
            from config import STOCK_PAIRS
            while True:
                for symbol in list(STOCK_PAIRS.values()):
                    await self.hub.run_full_scan(symbol)
                    # Random Jitter (60-120 seconds) - Strict Additive Guard
                    import random
                    await asyncio.sleep(random.uniform(60, 120))
                await asyncio.sleep(config.INTELLIGENCE_RECON_INTERVAL)

def log_trade(trade_data):
    """Helper to maintain trade_history.json without corruption."""
    file_path = config.TRADE_HISTORY_FILE
    history = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                history = json.load(f)
        except: history = []
    
    history.append(trade_data)
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=4)
