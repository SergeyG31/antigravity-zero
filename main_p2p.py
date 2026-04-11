import asyncio
import os
import subprocess
import time
from auth_manager import AuthManager
from scraper_engine import ScraperEngine
from ad_manager import ArbManager
from config import EXCHANGES, CRYPTO_PAIRS

class SmartCryptoOrchestrator:
    def __init__(self):
        self.auth_mgr = AuthManager()
        self.scraper = ScraperEngine(self.auth_mgr)
        self.arb_mgr = ArbManager(self.auth_mgr)
        self.running = True

    async def run_arb_loop(self):
        """Smart Crypto Specialist Loop (MEXC ONLY)."""
        from telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier()
        last_heartbeat = time.time()
        
        while self.running:
            # 1. EMERGENCY KILL-SWITCH
            if os.getenv('EMERGENCY_EXIT') == 'True' or os.path.exists('EMERGENCY_STOP'):
                print("🛑 EMERGENCY STOP DETECTED! Shutting down...")
                notifier.send_message("🚨 *EMERGENCY SHUTDOWN*: LiorBot is stopping now.")
                self.running = False
                break

            # 2. HEARTBEAT (Every Hour)
            if time.time() - last_heartbeat >= 3600:
                try:
                    mexc = self.auth_mgr.get_all_exchanges()['mexc']
                    bal = await mexc.fetch_balance()
                    usdt = bal['total'].get('USDT', 0)
                    open_count = len(self.arb_mgr.open_positions)
                    msg = f"💓 *LiorBot Heartbeat*\nBalance: {round(usdt, 2)} USDT\nActive Positions: {open_count}"
                    notifier.send_message(msg)
                    last_heartbeat = time.time()
                except Exception as e:
                    print(f"Heartbeat Error: {e}")

            print(f"[{time.strftime('%H:%M:%S')}] Monitoring {len(CRYPTO_PAIRS)} Crypto Pairs on MEXC...")
            
            # Refresh all crypto prices
            price_hub = await self.scraper.refresh_all_prices()
            
            # Execute Smart Crypto logic
            await self.arb_mgr.run_crypto_smart_logic(price_hub)

            from config import SCAN_TIMEOUT
            await asyncio.sleep(SCAN_TIMEOUT)

    async def run_intelligence_learning(self):
        """Background Task: Running Sentiment Monitor."""
        from trading_intelligence import TradingIntelligence
        monitor = TradingIntelligence.SentimentMonitor()
        
        # Start background sentiment cache warmer
        asyncio.create_task(monitor.background_recon())
        
        while self.running:
            await asyncio.sleep(3600) 

    async def start(self):
        print(f"🏛️ SMART CRYPTO AGENT: ACTIVATED.")
        print(f"Tracking: {', '.join(CRYPTO_PAIRS)}")
        
        from telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier()
        notifier.send_message(f"🚀 *Smart Crypto Agent*: ONLINE.\nAnalyzing {len(CRYPTO_PAIRS)} pairs on Binance/MEXC.")

        try:
            await asyncio.gather(
                self.run_arb_loop(),
                self.run_intelligence_learning()
            )
        finally:
            print("Cleaning up connections...")
            for ex in self.auth_mgr.get_all_exchanges().values():
                await ex.close()
            print("Smart Engine: Offline.")

if __name__ == "__main__":
    orchestrator = SmartCryptoOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        print("Shutdown requested...")
