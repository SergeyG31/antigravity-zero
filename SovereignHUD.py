import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import threading
import time
import asyncio
from auth_manager import AuthManager
from scraper_engine import ScraperEngine
from config import STOCK_PAIRS

class SovereignTerminalHUD:
    def __init__(self):
        # Initialize Core Engines
        self.auth_mgr = AuthManager()
        self.scraper = ScraperEngine(self.auth_mgr)
        self.running = True

        self.root = tk.Tk()
        self.root.title("🏛️ Antigravity: Sovereign Terminal HUD")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0a0a0a")
        
        # ... (GUI configuration remains same) ...
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", background="#0f0f0f", foreground="#00ff41", fieldbackground="#0f0f0f", font=("Courier", 10))
        self.style.configure("Treeview.Heading", background="#1a1a1a", foreground="#ffffff", font=("Courier", 11, "bold"))

        self.header = tk.Frame(self.root, bg="#1a1a1a", height=40)
        self.header.pack(fill="x", side="top", padx=5, pady=5)
        self.lbl_status = tk.Label(self.header, text="SYSTEM: MONITORING LIVE", bg="#1a1a1a", fg="#00ff41", font=("Courier", 10, "bold"))
        self.lbl_status.pack(side="left", padx=10)

        self.table_frame = tk.Frame(self.root, bg="#0a0a0a")
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Symbol", "WallStreet (Yahoo)", "Exchange (MEXC)", "Lag %", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.console_frame = tk.Frame(self.root, bg="#0a0a0a")
        self.console_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.console = scrolledtext.ScrolledText(self.console_frame, bg="#000000", fg="#00ff41", font=("Courier New", 10))
        self.console.pack(fill="both", expand=True)

        # Background Update Thread (Using Asyncio Integration)
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_async_loop, daemon=True).start()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.update_loop())

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)

    async def update_loop(self):
        while self.running:
            try:
                # 1. Fetch REAL prices from Yahoo vs MEXC
                self.log("📡 Fetching live prices (Yahoo vs MEXC)...")
                mexc_prices, yahoo_prices = await self.scraper.refresh_all_prices()
                
                # 2. Update GUI
                self.root.after(0, self.refresh_ui, mexc_prices, yahoo_prices)
                self.log("✅ Update Complete.")
            except Exception as e:
                self.log(f"⚠️ Scan Warning: {e}")
            
            await asyncio.sleep(15) # Scan every 15 seconds

    def refresh_ui(self, mexc_prices, yahoo_prices):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for token, real_ticker in STOCK_PAIRS.items():
            y_price = yahoo_prices.get(token, 0.0)
            token_price_dict = mexc_prices.get(token, {})
            # Handle different nested structures if necessary
            m_price = token_price_dict.get('mexc', {}).get('sell', 0.0) if isinstance(token_price_dict, dict) else 0.0
            
            lag = "N/A"
            status = "🌐 OFFLINE"
            
            if y_price > 0 and m_price > 0:
                lag_val = round(((y_price - m_price) / m_price) * 100, 3)
                lag = f"{lag_val}%"
                status = "STABLE" if lag_val < 0.1 else "🔥 ARB OPPORTUNITY"
            
            # Formatting for display
            display_y = f"${y_price}" if y_price > 0 else "OFFLINE"
            display_m = f"${m_price}" if m_price > 0 else "OFFLINE"
            
            self.tree.insert("", tk.END, values=(token, display_y, display_m, lag, status))


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SovereignTerminalHUD()
    app.run()
