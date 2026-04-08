import asyncio
import os
import subprocess
import time
from auth_manager import AuthManager
from scraper_engine import ScraperEngine
from ad_manager import ArbManager
from config import EXCHANGES, STOCK_PAIRS

class MexcStockOrchestrator:
    def __init__(self):
        self.auth_mgr = AuthManager()
        self.scraper = ScraperEngine(self.auth_mgr)
        self.arb_mgr = ArbManager(self.auth_mgr)
        self.running = True

    async def run_arb_loop(self):
        """MEXC Stock Specialist Loop."""
        while self.running:
            print(f"[{time.strftime('%H:%M:%S')}] Monitoring {len(STOCK_PAIRS)} Stocks on MEXC...")
            
            # Refresh both: MEXC Token Prices + Real NYSE/NASDAQ Stocks
            price_hub, stock_hub = await self.scraper.refresh_all_prices()
            
            # Execute Wall Street Lag strategy (ONLY Stocks)
            await self.arb_mgr.run_stock_lag_logic(price_hub, stock_hub)

            await asyncio.sleep(10)

    async def run_intelligence_learning(self):
        """Background Task: Running Sentiment Monitor and AI Strategy Learner."""
        from trading_intelligence import TradingIntelligence
        learner = TradingIntelligence.StrategyLearner()
        monitor = TradingIntelligence.SentimentMonitor()
        
        # Start background sentiment cache warmer
        asyncio.create_task(monitor.background_recon())
        
        while self.running:
            # Run reflective learning every few hours or based on config
            await learner.learn_from_history()
            await asyncio.sleep(3600) # Once per hour analysis

    async def run_report_loop(self):
        """Daily Reporting."""
        await asyncio.sleep(60)

    def launch_dashboard(self):
        """Tactical Dashboard."""
        import webbrowser
        import sys
        print("Launching MEXC Specialist Dashboard on Port 8505...")
        try:
            # Use current python to run streamlit module for environment consistency
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8505"])
            time.sleep(3)
            webbrowser.open("http://localhost:8505")
        except Exception as e:
            print(f"⚠️ Could not launch dashboard automatically: {e}")
            print("Try running: streamlit run dashboard.py --server.port 8505")

    async def start(self):
        print(f"🏛️ MEXC STOCK SPECIALIST: ACTIVATED.")
        print(f"Tracking: {', '.join(STOCK_PAIRS.values())}")
        
        self.launch_dashboard()
        
        try:
            await asyncio.gather(
                self.run_arb_loop(),
                self.run_intelligence_learning(),
                self.run_report_loop()
            )
        finally:
            print("Cleaning up connections...")
            for ex in self.auth_mgr.get_all_exchanges().values():
                await ex.close()
            print("Sovereign Engine: Offline.")

if __name__ == "__main__":
    orchestrator = MexcStockOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        print("Shutdown requested...")
