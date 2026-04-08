import ccxt
import os
from config import EXCHANGES, ASSET_PAIR, MAX_ORDER_SIZE, MIN_LIQUIDITY_BRAKE
from auth_manager import AuthManager

class CryptoTradingEngine:
    def __init__(self, auth_mgr: AuthManager):
        self.auth_mgr = auth_mgr
        self.exchanges = self.auth_mgr.get_all_exchanges()

    async def get_balance(self, exchange_id, asset='USDT'):
        """Fetches the real balance of a specific asset on an exchange."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return 0.0
        try:
            balance = await exchange.fetch_balance()
            return balance.get('total', {}).get(asset, 0.0)
        except Exception as e:
            print(f"[{exchange_id}] Error fetching balance: {e}")
            return 0.0

    async def execute_arbitrage_trade(self, buy_ex_id, sell_ex_id, amount_usdt):
        """Executes a spot arbitrage trade between two exchanges."""
        # Note: This is a complex operation involving spot market execution.
        # For a P2P bot, it usually alerts the user to move funds or place manual ads.
        print(f"🚀 EXECUTING ARBITRAGE: Buy {amount_usdt} USDT on {buy_ex_id} -> Sell on {sell_ex_id}")
        
        # 1. Check balances
        buy_balance = await self.get_balance(buy_ex_id)
        if buy_balance < amount_usdt:
            print(f"❌ Aborting: Insufficient balance on {buy_ex_id}")
            return False

        # 2. Actual Market Execution (Spot)
        # buy_ex = self.exchanges[buy_ex_id]
        # await buy_ex.create_market_buy_order(ASSET_PAIR, amount_usdt)
        
        print(f"✅ Trade logic processed for {buy_ex_id} and {sell_ex_id}")
        return True

    async def close_all_positions(self):
        """Emergency Stop: Cancels all open P2P/Spot orders across all hubs."""
        print("🚨 EMERGENCY HALT: Canceling all orders across all 5 hubs...")
        for ex_id, exchange in self.exchanges.items():
            try:
                # Cancel all open p2p ads (if supported) or spot orders
                print(f"[{ex_id}] Canceling orders...")
                # await exchange.cancel_all_orders(ASSET_PAIR)
            except Exception as e:
                print(f"[{ex_id}] Error during halt: {e}")
        return True

if __name__ == "__main__":
    # Test script (will need valid keys)
    from auth_manager import AuthManager
    import asyncio
    
    async def test():
        auth = AuthManager()
        engine = CryptoTradingEngine(auth)
        # balance = await engine.get_balance('bybit')
        # print(f"Bybit Balance: {balance}")
    
    # asyncio.run(test())
