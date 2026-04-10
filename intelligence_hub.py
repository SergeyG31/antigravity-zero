import warnings
warnings.filterwarnings("ignore") 

import asyncio
import os
import google.generativeai as genai
import random
from config import CRYPTO_PAIRS

class MarketIntelligenceHub:
    def __init__(self):
        # Configure Gemini API for News Sentiment Analysis
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.ai_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        else:
            self.ai_model = None

    async def fetch_latest_news(self, ticker_symbol):
        """Fetches top crypto news for AI analysis."""
        import requests
        try:
            # Fetch all top news (more stable than filtering by category)
            url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                json_data = response.json()
                news_list = json_data.get('Data', [])
                
                # Double check that we received a list
                if not isinstance(news_list, list):
                    return ""
                
                combined_news = ""
                # Take top 10 news items to give the AI context of the whole market
                for item in news_list[:10]:
                    title = item.get('title', '')
                    body = item.get('body', '')
                    combined_news += f"Title: {title}\nSummary: {body}\n\n"
                return combined_news
            return ""
        except Exception as e:
            print(f"[Crypto News API] Network Error: {e}")
            return ""

    async def analyze_sentiment(self, ticker, text_content):
        """Uses Gemini AI with the Crypto dictionary to assess Market Alpha."""
        if not self.ai_model or not text_content: return "NEUTRAL", 0
        
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            keywords_path = os.path.join(base_dir, "crypto_dictionary.md")
            with open(keywords_path, "r", encoding="utf-8") as f:
                sentiment_dict = f.read()
        except Exception:
            sentiment_dict = "(Crypto Dictionary not found)"

        prompt = f"""
        You are a Master Crypto Quant Trader.
        Analyze the following news and social media sentiment for '{ticker}':
        
        {text_content}
        
        ---
        GUIDE DICTIONARY:
        {sentiment_dict}
        ---
        
        Assess if there is a breakout opportunity. 
        Focus on 'Smart Money' signs vs 'Retail FOMO'.
        Output Format:
        SIGNAL: [BULLISH / BEARISH / NEUTRAL]
        SCORE: [1 to 10]
        RATIONALE: (One sentence)
        """
        
        try:
            response = self.ai_model.generate_content(prompt)
            result = response.text.upper()
            
            signal = "NEUTRAL"
            if "BULLISH" in result: signal = "BULLISH"
            elif "BEARISH" in result: signal = "BEARISH"
            
            import re
            numbers = re.findall(r'\d+', result)
            score = int(numbers[0]) if numbers else 0
            
            return signal, score
        except Exception as e:
            print(f"[AI Crypto Scanner] Error: {e}")
            return "NEUTRAL", 0

    async def run_full_scan(self, ticker):
        """Executes the full Pipeline: News -> AI Analysis."""
        print(f"🔎 Running Deep Crypto Recon on {ticker}...")
        combined_text = await self.fetch_latest_news(ticker)
        
        if not combined_text:
            return "NO_DATA", 0

        # Anti-Ban Jitter and API Quota Management
        delay = random.uniform(1.5, 3.5)
        await asyncio.sleep(delay)
            
        # Final Agent Assessment
        signal, score = await self.analyze_sentiment(ticker, combined_text)
        print(f"🤖 [AI CRYPTO REPORT] {ticker}: {signal} (Conviction: {score}/10)")
        return signal, score

if __name__ == "__main__":
    hub = MarketIntelligenceHub()
    # Test Run on BTC
    asyncio.run(hub.run_full_scan("BTC"))
