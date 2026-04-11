import os
import asyncio
import ccxt.pro as ccxt
from dotenv import load_dotenv

async def run_diagnostic():
    load_dotenv()
    print("🔍 Inspecting All MEXC Balances...")
    
    api_key = os.getenv('MEXC_API_KEY')
    api_secret = os.getenv('MEXC_API_SECRET')
    
    try:
        exchange = ccxt.mexc({
            'apiKey': api_key,
            'secret': api_secret,
        })
        
        balance = await exchange.fetch_balance()
        print("\n--- Non-Zero Balances ---")
        for asset, total in balance['total'].items():
            if total > 0:
                print(f"💰 {asset}: {total}")
        
        print("\n--- Diagnostic Complete ---")
        await exchange.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
