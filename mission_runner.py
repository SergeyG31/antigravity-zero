#!/usr/bin/env python3
import asyncio
import sys
import os

# ייבוא מהחבילה המקומית בתוך ה-workspace
from skills.antigravity_os import ag_os
from skills.universal_scraper import scraper
from skills.reflector import reflector

async def run_mission():
    project_name = "MEXC_Stock_Arbitrage_P2P"
    mission_topic = "High-Performance Arbitrage between NYSE and MEXC Tokenized Assets"
    
    ag_os.log_event("MISSION_START", f"Initializing mission: {mission_topic}")
    
    # 1. Analyze task using AG-OS
    decision = await ag_os.analyze_task(mission_topic, {"platform": "MEXC", "base": "USDT"})
    ag_os.log_event("DECISION", f"OS recommended to {decision['decision']}")
    
    # 2. Gather data using Universal Scraper
    ag_os.log_event("SCRAPER", "Fetching initial market data for MSFT and TSLA...")
    msft_price = scraper.fetch_stock("MSFT")
    tsla_price = scraper.fetch_stock("TSLA")
    
    ag_os.log_event("DATA", f"MSFT: ${msft_price} | TSLA: ${tsla_price}")
    
    # 3. Simulate news gathering
    news_sample = scraper.fetch_web_content("https://finance.yahoo.com/quote/MSFT")
    ag_os.log_event("SCRAPER", f"Gathered {len(news_sample)} chars of news content.")
    
    # 4. Save insight to OS memory/knowledge
    insight = f"Initial MSFT price at mission start: ${msft_price}. Market sentiment scan complete."
    ag_os.save_insight(project_name, insight)
    ag_os.log_event("MEMORY", "Insight saved to global mission knowledge base.")
    
    # 5. Self-Reflection
    reflection = reflector.review_logs("antigravity_core.log")
    ag_os.log_event("REFLECTOR", reflection)

if __name__ == "__main__":
    asyncio.run(run_mission())
