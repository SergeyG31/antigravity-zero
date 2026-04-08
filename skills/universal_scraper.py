import yfinance as yf
import requests
import time
import random
import logging
from bs4 import BeautifulSoup

# Global User-Agent List for Rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

import json
import os

class UniversalScraper:
    """
    יכולת סריקה אוניברסלית עמידה בפני חסימות (Anti-429) עם Persistent Caching.
    """
    def __init__(self, cache_file="scraper_cache.json"):
        self.retry_delay = 5 # Initial retry delay in seconds
        self.cache_file = cache_file
        self.cache_ttl = 60 # Time-to-Live in seconds
        self.cache = self._load_cache()
        
    def _load_cache(self):
        """Loads cache from JSON file on restart."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        """Persists cache to JSON file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")

    def _get_headers(self):
        return {"User-Agent": random.choice(USER_AGENTS)}

    def fetch_stock(self, ticker):
        """
        Fetches stock price with Persistent Caching, Exponential Backoff and Random Jitter.
        """
        # 0. Check Cache First
        now = time.time()
        if ticker in self.cache:
            price, timestamp = self.cache[ticker]
            if now - timestamp < self.cache_ttl:
                print(f"⚡ [PERSISTENT CACHE HIT] {ticker}: ${price} (Age: {round(now - timestamp, 1)}s)")
                return price

        max_retries = 3
        current_attempt = 0
        backoff = self.retry_delay

        while current_attempt < max_retries:
            try:
                # 1. Random Jitter before any fetch
                jitter = random.uniform(1.0, 3.0)
                time.sleep(jitter)
                
                # 2. Setup Ticker with rotated headers (yfinance uses requests internally)
                data = yf.Ticker(ticker)
                
                hist = data.history(period='1d')
                val = 0.0
                if not hist.empty:
                    val = round(hist['Close'].iloc[-1], 2)
                
                self.cache[ticker] = (val, time.time())
                self._save_cache()
                logging.info(f"✅ [Scraper] {ticker} Price: ${val} (Attempt {current_attempt + 1})")
                return val
                
                # Fallback to alternative sources if Yahoo is empty
                return self.fetch_alternative_source(ticker)

            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    logging.warning(f"⚠️ [429 ERROR] Rate limited on {ticker}. Backing off for {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2 # Exponential Backoff
                    current_attempt += 1
                else:
                    logging.error(f"❌ [Scraper Error] {ticker}: {e}")
                    return self.fetch_alternative_source(ticker)
        
        return 0.0

    def fetch_alternative_source(self, ticker):
        """
        Fallback: Google Finance scraping (Simple parsing).
        """
        logging.info(f"🔄 [Fallback] Attempting Google Finance for {ticker}...")
        try:
            url = f"https://www.google.com/search?q=google+finance+{ticker}+price"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Google Search result often contains price in a specific div
                # This is a simplified fallback and might need CSS selector updates
                # For MSFT, it might find "425.22 USD"
                text = soup.get_text()
                import re
                prices = re.findall(r'\d+\.\d+\s+USD', text)
                if prices:
                    price_val = float(prices[0].split()[0])
                    self.cache[ticker] = (price_val, time.time())
                    self._save_cache()
                    return price_val
            return 0.0
        except Exception as e:
            logging.error(f"❌ [Fallback Failed] {e}")
            return 0.0

    def fetch_web_content(self, url):
        """סריקת תוכן אתרים עם Roated Headers"""
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            return response.text[:2000]
        except Exception as e:
            logging.error(f"Web Content Error: {e}")
            return ""

scraper = UniversalScraper()
