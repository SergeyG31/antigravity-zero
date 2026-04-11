import os
import asyncio
import ccxt.pro as ccxt
from dotenv import load_dotenv

async def liquidate():
    load_dotenv()
    mexc = ccxt.mexc({
        'apiKey': os.getenv('MEXC_API_KEY'),
        'secret': os.getenv('MEXC_API_SECRET'),
    })
    
    for coin in ['SUI', 'AVAX']:
        print(f"🔄 Checking {coin}...")
        try:
            bal = await mexc.fetch_balance()
            amt = bal['total'].get(coin, 0)
            if amt > 0:
                print(f"🚀 Selling {amt} {coin}...")
                # Use market sell
                await mexc.create_market_sell_order(f"{coin}/USDT", amt)
                print(f"✅ {coin} Sold successfully.")
            else:
                print(f"ℹ️ No {coin} found in balance.")
        except Exception as e:
            print(f"❌ Failed to sell {coin}: {e}")
            
    await mexc.close()

if __name__ == "__main__":
    asyncio.run(liquidate())
