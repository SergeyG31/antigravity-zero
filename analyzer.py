import pandas as pd
import numpy as np

class PatternAnalyzer:
    def __init__(self):
        pass

    def calculate_rsi(self, series, period=14):
        """Manual RSI implementation using pandas."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def detect_patterns(self, df):
        """Detects signals using pure pandas (no pandas_ta required)."""
        if df.empty or len(df) < 20:
            return []

        signals = []
        close = df['Close']

        # 1. Technical Indicators calculation (Manual)
        df['RSI'] = self.calculate_rsi(close)
        df['SMA_20'] = close.rolling(window=20).mean()
        df['SMA_100'] = close.rolling(window=100).mean()
        
        # 2. Simple Bullish Signal Strategy
        latest_rsi = df['RSI'].iloc[-1]
        prev_rsi = df['RSI'].iloc[-2]
        latest_close = close.iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1]

        # RSI Oversold Signal
        if latest_rsi < 30:
            signals.append(f"Oversold RSI ({latest_rsi:.2f})")
        
        # Price crossing SMA_20 upwards
        if latest_close > sma_20 and close.iloc[-2] <= df['SMA_20'].iloc[-2]:
            signals.append("Price crossed above SMA 20")

        # 3. Simple Candlestick logic (Manual)
        # Bullish Engulfing: Close > Prev Open and Open < Prev Close and Prev was bearish
        if len(df) > 2:
            curr = df.iloc[-1]
            prev = df.iloc[-2]
            if curr['Close'] > prev['Open'] and curr['Open'] < prev['Close'] and prev['Close'] < prev['Open']:
                signals.append("Potential Bullish Engulfing")

        return signals
