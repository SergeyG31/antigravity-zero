import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
import ccxt.pro as ccxt

async def run_diagnostic():
    load_dotenv()
    print("🧪 [DIAGNOSTIC] Starting System Health Check...")
    
    # 1. Check Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = model.generate_content("Health check: Reply with 'OK'")
            print(f"✅ [GEMINI AI] Connected. Response: {response.text.strip()}")
        except Exception as e:
            print(f"❌ [GEMINI AI] Failed: {e}")
    else:
        print("❌ [GEMINI AI] Missing API Key in .env")

    # 2. Check MEXC
    mexc_key = os.getenv('MEXC_API_KEY')
    mexc_secret = os.getenv('MEXC_API_SECRET')
    if mexc_key and mexc_secret:
        try:
            mexc = ccxt.mexc({
                'apiKey': mexc_key,
                'secret': mexc_secret,
            })
            balance = await mexc.fetch_balance()
            usdt_bal = balance.get('USDT', {}).get('free', 0.0)
            print(f"✅ [MEXC EXCHANGE] Connected. USDT Balance: {usdt_bal}")
            await mexc.close()
        except Exception as e:
            print(f"❌ [MEXC EXCHANGE] Connection Failed: {e}")
    else:
        print("❌ [MEXC EXCHANGE] Missing Credentials in .env")

    # 3. Check Telegram
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if tg_token:
        print(f"✅ [TELEGRAM] Bot Token found.")
    else:
        print("❌ [TELEGRAM] Missing Bot Token in .env")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
