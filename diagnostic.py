import os
import asyncio
import ccxt.pro as ccxt
from dotenv import load_dotenv

async def run_diagnostic():
    load_dotenv()
    print("🔍 Starting LiorBot MEXC Diagnostic...")
    
    api_key = os.getenv('MEXC_API_KEY')
    api_secret = os.getenv('MEXC_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ ERROR: MEXC API Keys missing in .env file!")
        return

    try:
        # Initialize MEXC
        exchange = ccxt.mexc({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        
        print(f"📡 Connecting to MEXC...")
        balance = await exchange.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        
        print(f"✅ Connection Successful!")
        print(f"💰 Account Balance: {usdt_balance} USDT")
        
        if usdt_balance < 10:
            print("⚠️ Warning: Balance is low. Minimum trade is $10.")
        else:
            print("🚀 Bot is authorized and ready to trade!")
            
        await exchange.close()
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
