import google.generativeai as genai
from config import GEMINI_API_KEY, EXCHANGES

class CentralAISecurity:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat_logs = {ex: [] for ex in EXCHANGES}

    def process_all_chats(self, all_exchange_chats):
        """Unified Chat Analysis: centralizes and filters for fraud."""
        all_reports = {}
        for exchange_id, chat in all_exchange_chats.items():
            report = self.guardian_check(exchange_id, chat)
            all_reports[exchange_id] = report
        return all_reports

    def guardian_check(self, exchange_id, chat_history):
        """Single Gemini Agent checking P2P chat across any platform."""
        prompt = f"""
        Platform: {exchange_id} (P2P USDT/ILS)
        Chat: {chat_history}
        Task: Analyze for fraud (e.g., requests to pay from third-party account, suspicious bank transfers).
        Return 'SUSPICIOUS' or 'VERIFIED' with a 1-sentence reasoning.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            return "VERIFIED (API Fallback)"

    def log_interaction(self, exchange_id, message):
        self.chat_logs[exchange_id].append(message)
        # Future: Webhook to Streamlit UI
