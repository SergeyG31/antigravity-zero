import yfinance as yf
import pandas as pd
import requests
import time
from functools import wraps
from config import ALPHA_VANTAGE_API_KEY, SYMBOL

def retry(retries=3, delay=2):
    """Decorator for retrying functions on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            iters = 0
            while iters < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    iters += 1
                    print(f"Error calling {func.__name__} (attempt {iters}/{retries}): {e}")
                    if iters == retries:
                        print(f"Final failure after {retries} attempts.")
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class DataManager:
    def __init__(self):
        self.alpha_vantage_url = 'https://www.alphavantage.co/query'

    @retry(retries=3, delay=2)
    def fetch_yfinance_data(self, symbol=SYMBOL, period='1d', interval='5m'):
        """Fetches historical data using yfinance."""
        data = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
        if data.empty:
            raise ValueError(f"No data returned for {symbol}")
        return data

    @retry(retries=2, delay=1)
    def fetch_alpha_vantage_quote(self, symbol=SYMBOL):
        """Fetches a single real-time quote using Alpha Vantage."""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(self.alpha_vantage_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'Global Quote' in data:
            return data['Global Quote']
        elif 'Note' in data:
            print(f"Alpha Vantage API limit reached: {data['Note']}")
        return None

    def get_combined_data(self, symbol=SYMBOL):
        """Combines historical and real-time data for analysis."""
        try:
            df = self.fetch_yfinance_data(symbol)
            return df
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
