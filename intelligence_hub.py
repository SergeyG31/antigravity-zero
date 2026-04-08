import warnings
warnings.filterwarnings("ignore") # Suppress Gemini deprecation warnings

import asyncio
import os
import google.generativeai as genai
from finvizfinance.screener.overview import Overview
from newspaper import Article
import random
from config import STOCK_PAIRS
import yfinance as yf

try:
    from ntscraper import Nitter
    NTSCRAPER_AVAILABLE = True
except ImportError:
    NTSCRAPER_AVAILABLE = False

class MarketIntelligenceHub:
    def __init__(self):
        # Configure Gemini API for News Sentiment Analysis
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.ai_model = None

    async def get_finviz_top_gainers(self):
        """Uses finvizfinance to find stocks moving fast right now."""
        try:
            foverview = Overview()
            filters_dict = {'Signal': 'Top Gainers', 'Volume': 'Over 1 Million'}
            foverview.set_filter(filters_dict=filters_dict)
            df = foverview.screener_view()
            
            target_tickers = list(STOCK_PAIRS.values())
            matches = df[df['Ticker'].isin(target_tickers)]
            
            if not matches.empty:
                print(f"📈 [FINVIZ] Found {len(matches)} of our tokens in Top Gainers!")
                return matches['Ticker'].tolist()
            return []
        except Exception as e:
            print(f"[FINVIZ] Engine error: {e}")
            return []

    async def fetch_latest_news(self, ticker_symbol):
        """Uses yfinance to fetch news URLs for a ticker reliably."""
        try:
            stock = yf.Ticker(ticker_symbol)
            news_items = stock.news
            
            urls = []
            if isinstance(news_items, list):
                for item in news_items[:3]: # Top 3 recent articles
                    link = item.get('link')
                    if link: urls.append(link)
            return urls
        except Exception as e:
            print(f"[News Scraper] Error fetching news for {ticker_symbol}: {e}")
            return []


    async def scrape_article_text(self, url):
        """Uses newspaper3k to extract text from a news URL."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text[:2000] # Return top 2000 chars for AI context
        except Exception as e:
            # print(f"[Scraper] Failed to read {url}")
            return ""

    async def analyze_sentiment(self, ticker, text_content):
        """Uses Gemini AI to assess if the news indicates a strong BUY."""
        if not self.ai_model or not text_content: return "NEUTRAL", 0
        
        try:
            with open("/Users/sergeygalayev/Desktop/LiorBot_Improved/bullish_keywords.md", "r", encoding="utf-8") as f:
                sentiment_dict = f.read()
        except Exception:
            sentiment_dict = "(Dictionary file not found)"

        prompt = f"""
        You are an elite high-frequency trading analyst. 
        Read the following recent news for stock '{ticker}':
        
        {text_content}
        
        ---
        Use the following Bullish Sentiment Dictionary to guide your analysis:
        {sentiment_dict}
        ---
        
        Based ONLY on the news text and how it matches the concepts in the dictionary, assess the market sentiment.
        Reply strictly in this format:
        SIGNAL: [BULLISH / BEARISH / NEUTRAL]
        SCORE: [1 to 10]
        """
        
        try:
            response = self.ai_model.generate_content(prompt)
            result = response.text.upper()
            
            signal = "NEUTRAL"
            score = 0
            
            if "BULLISH" in result: signal = "BULLISH"
            elif "BEARISH" in result: signal = "BEARISH"
            
            # Simple grab of the score digit
            import re
            numbers = re.findall(r'\d+', result)
            if numbers: score = int(numbers[-1])
            
            return signal, score
        except Exception as e:
            print(f"[AI Scanner] Error: {e}")
            return "NEUTRAL", 0

    async def scrape_twitter_sentiment(self, ticker):
        """Uses ntscraper to silently pull current X (Twitter) sentiment without API keys."""
        if not NTSCRAPER_AVAILABLE:
            return ""
        try:
            print(f"🐦 [Twitter] Scraping latest mentions for {ticker}...")
            scraper = Nitter(log_level=1, skip_instance_check=False)
            # Find 5 recent tweets discussing the stock
            tweets = scraper.get_tweets(f"${ticker}", mode='term', number=5)
            
            tweet_text = ""
            if tweets and 'tweets' in tweets:
                for t in tweets['tweets']:
                    tweet_text += t.get('text', '') + "\n"
            return tweet_text
        except Exception as e:
            print(f"[Twitter Scraper] Error: {e}")
            return ""

    async def run_full_scan(self, ticker):
        """Executes the full Pipeline: News -> Scrape -> AI Analysis."""
        print(f"🔎 Running Deep Recon on {ticker}...")
        urls = await self.fetch_latest_news(ticker)
        
        if not urls:
            return "NO_DATA", 0

        combined_text = ""
        
        # 1. Fetch News
        for url in urls:
            text = await self.scrape_article_text(url)
            combined_text += text + "\n\n"
            
        # 2. Fetch Twitter Data
        twitter_text = await self.scrape_twitter_sentiment(ticker)
        if twitter_text:
            combined_text += "\n--- TWITTER SENTIMENT ---\n" + twitter_text
            
        # 3. Secure DevOps Anti-Ban Logic
        delay = random.uniform(2.5, 6.5)
        print(f"🛡️ [Anti-Ban] Sleeping for {round(delay, 1)}s to mimic human browsing...")
        await asyncio.sleep(delay)
            
        # 4. Final Agent Assessment
        signal, score = await self.analyze_sentiment(ticker, combined_text)
        print(f"🤖 [AI REPORT] {ticker}: {signal} (Conviction: {score}/10)")
        return signal, score

if __name__ == "__main__":
    hub = MarketIntelligenceHub()
    # Test Run on TSLA
    asyncio.run(hub.run_full_scan("TSLA"))
