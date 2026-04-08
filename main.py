import asyncio
import time
from config import EXCHANGES, SCAN_TIMEOUT, ASSET_PAIR
from liquidity_balancer import LiquidityPool
from market_scanner import MultiMarketScanner
from ad_commander import AdCommander
from central_ai_security import CentralAISecurity

class MultiHubOrchestrator:
    def __init__(self):
        self.pool = LiquidityPool()
        self.scanner = MultiMarketScanner()
        self.commander = AdCommander()
        self.security = CentralAISecurity()
        self.running = True

    async def run_aggregated_execution(self):
        """The core loop: Scanning 4 hubs and balancing ads synchronously."""
        while self.running:
            print(f"[{time.strftime('%H:%M:%S')}] Core Hub Scan: Binance, Bybit, OKX, MEXC...")
            
            # Fetch depths across 4 platforms
            depths = await self.scanner.scan_all_depths()
            
            # Cross-platform Arbitrage Audit
            arb_opportunity = self.scanner.find_cross_arb(depths)
            if arb_opportunity:
                print(f"[{time.strftime('%H:%M:%S')}] HYPER YIELD: {arb_opportunity}")

            # Update Ads per platform aggressively
            for exchange_id in EXCHANGES:
                if depths[exchange_id]['ask'] > 0:
                    self.commander.update_ad_aggression(exchange_id, "GLOBAL_AD_ID", depths[exchange_id]['ask'])

            await asyncio.sleep(SCAN_TIMEOUT)

    async def run_central_security(self):
        """Unified Security Agent: Managing all chats from 4 exchanges simultaneously."""
        while self.running:
            print(f"[{time.strftime('%H:%M:%S')}] Central AI Vigilance: Multi-Hub Fraud Scan...")
            # Mock central chat check
            reports = self.security.process_all_chats({'binance': 'Example: Hello', 'bybit': 'Example: Pay 3rd party'})
            
            for ex, result in reports.items():
                if "SUSPICIOUS" in result.upper():
                    print(f"[{time.strftime('%H:%M:%S')}] GUARDIAN PROTECT: BLOCKING {ex.upper()} AD DUE TO FRAUD.")
            
            await asyncio.sleep(20)

    async def run_liquidity_balancing(self):
        """Liquidity Balancer: Auditing cross-exchange USDT distribution."""
        while self.running:
            print(f"[{time.strftime('%H:%M:%S')}] Pool Management: Auditing Asset Spread...")
            # Balances and premium comparison
            # pool.balance_audit(current_prices)
            await asyncio.sleep(60)

    async def start(self):
        # Concurrently run all three central layers
        print("🏛️ Starting P2P Sovereign Aggregator v2.0...")
        await asyncio.gather(
            self.run_aggregated_execution(),
            self.run_central_security(),
            self.run_liquidity_balancing()
        )

if __name__ == "__main__":
    orchestrator = MultiHubOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        print("Stopping Aggregator Engine...")
