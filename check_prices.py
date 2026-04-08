import asyncio
import yfinance as yf
import ccxt
import time

async def check_arb():
    print(f"[{time.strftime('%H:%M:%S')}] Manual Price Audit...")
    
    # 1. Yahoo Finance (Real Market)
    msft_stock = yf.Ticker("MSFT")
    real_price = msft_stock.history(period='1d', interval='1m')['Close'].iloc[-1]
    print(f"📊 [Yahoo Finance] MSFT: ${real_price}")

    # 2. MEXC (Tokenized)
    mexc = ccxt.mexc()
    try:
        ticker = await asyncio.to_thread(mexc.fetch_ticker, 'MSFTON/USDT')
        token_price = ticker['last']
        print(f"💹 [MEXC] MSFTON: ${token_price}")
        
        diff = ((real_price - token_price) / token_price) * 100
        print(f"🎯 Lag Deviation: {round(diff, 4)}%")
    except Exception as e:
        print(f"❌ MEXC Fetch Failed: {e}")
    finally:
        await mexc.close()

if __name__ == "__main__":
    asyncio.run(check_arb())
