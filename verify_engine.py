import asyncio
import os
from auth_manager import AuthManager
from scraper_engine import ScraperEngine
from dotenv import load_dotenv

async def verify_realtime_data():
    load_dotenv()
    print("📡 [VERIFICATION] Fetching RAW market data from hubs...")
    auth = AuthManager()
    scraper = ScraperEngine(auth)
    
    # Check MEXC specific stock token
    price_hub, stock_hub = await scraper.refresh_all_prices()
    
    print("\n--- LIVE MARKET DATA SNAPSHOT ---")
    for symbol, price in stock_hub.items():
        if price > 0:
            print(f"✅ {symbol}: ${price} (Live from Scraper)")
        else:
            print(f"❌ {symbol}: $0.00 (Failed or Closed Market)")
            
    # Check P2P Spread
    matrix = scraper.calculate_spread_matrix()
    print("\n--- P2P CONNECTION MATRIX ---")
    print(matrix[['Symbol', 'Exchange', 'Ask (Sell)']].head(10))
    
    # Check Gemini one last time
    from central_ai_security import CentralAISecurity
    security = CentralAISecurity()
    report = security.guardian_check("Test", "Is the bot connected?")
    print(f"\n--- AI BRAIN CHECK ---")
    print(f"Intelligence: {report}")

if __name__ == "__main__":
    asyncio.run(verify_realtime_data())
