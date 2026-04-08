import asyncio
import os
import sys

# Add skills to path
sys.path.append("/Users/sergeygalayev/Documents/antigravity_skills")

try:
    from AntigravityCore import AntigravityCore
except ImportError:
    # Fallback to local recreation if needed
    print("Could not import AntigravityCore, running direct test.")
    from telegram_notifier import TelegramNotifier
    notifier = TelegramNotifier()
    notifier.send_message("🚀 (Direct Test) Antigravity Execution: BUY TSLAON/USDT @ 350.5")
    sys.exit(0)

async def test_alert():
    core = AntigravityCore()
    print("Executing Mock Trade for Telegram Test...")
    await core.execute_mission_trade("TSLAON/USDT", "BUY", 350.5)
    await core.close()

if __name__ == "__main__":
    asyncio.run(test_alert())
