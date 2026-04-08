import os
import asyncio
import ccxt.pro as ccxt  # Pro version for high-speed Websockets
from dotenv import load_dotenv

class P2PExchangeAggregator:
    def __init__(self):
        load_dotenv()
        self.exchanges = {}
        self.status = {}
        self._init_exchanges()

    def _init_exchanges(self):
        """Initializes all 4 hubs with credentials from .env."""
        configs = {
            'bybit': {
                'apiKey': os.getenv('BYBIT_API_KEY'),
                'secret': os.getenv('BYBIT_API_SECRET'),
                'enableRateLimit': True,
            },
            'okx': {
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_API_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'enableRateLimit': True,
            },
            'binance': {
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_API_SECRET'),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            },
            'mexc': {
                'apiKey': os.getenv('MEXC_API_KEY'),
                'secret': os.getenv('MEXC_API_SECRET'),
                'enableRateLimit': True,
            }
        }

        for name, config in configs.items():
            if not config['apiKey']:
                self.status[name] = "Missing API Key ⚠️"
                continue
            try:
                # Initialize using CCXT Pro factory
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class(config)
                self.status[name] = "Initialized"
            except Exception as e:
                self.status[name] = f"Error: {str(e)}"

    async def check_connections(self):
        """Validates API keys by fetching account balances."""
        results = {}
        for name, client in self.exchanges.items():
            try:
                # For CCXT Pro, some methods might need await
                balance = await client.fetch_balance()
                results[name] = "Connected ✅"
            except Exception as e:
                results[name] = f"Authentication Failed ❌: {str(e)}"
        return results

    async def shutdown(self):
        """Closes all Websocket connections cleanly."""
        for client in self.exchanges.values():
            await client.close()

if __name__ == "__main__":
    aggregator = P2PExchangeAggregator()
    loop = asyncio.get_event_loop()
    print("Initializing P2P Multi-Exchange Connections...")
    res = loop.run_until_complete(aggregator.check_connections())
    for ex, stat in res.items():
        print(f"{ex.upper()}: {stat}")
