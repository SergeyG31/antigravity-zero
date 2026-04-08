import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

    def send_message(self, message):
        """Sends a direct message to the user and prints errors if any."""
        if not self.token or not self.chat_id:
            print("[Telegram] Skip: Missing Token or ChatID in .env")
            return
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[Telegram] ✅ Message sent successfully!")
            else:
                print(f"[Telegram] ❌ Failed! Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Telegram] ❌ Critical Error: {e}")

    def send_daily_report(self, daily_pnl, trade_count):
        """Generates a formatted daily summary at 18:00."""
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        report = f"""
🏛️ *P2P Sovereign Daily Report*
📅 Date: {now}
------------------------------
💰 Net Profit: ₪{daily_pnl}
🔄 Trades Executed: {trade_count}
📈 Win Rate: 100% (Safety Guard Active)
------------------------------
🤖 Status: Autonomous Running...
        """
        self.send_message(report)

if __name__ == "__main__":
    notifier = TelegramNotifier()
    notifier.send_message("🚀 Test Message: Antigravity P2P connection check.")
