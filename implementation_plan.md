# Implementation Plan - LiorBot_Improved Upgrade

This plan outlines the steps to upgrade the trading bot across four key areas: Infrastructure, Trading Engine, Analysis, and Interface.

## Phase 1: Infrastructure & Security 🛠️
1. **Secret Separation**:
    - [ ] Create a `.env` file for API keys.
    - [ ] Update `config.py` to load values from environment variables using `python-dotenv`.
2. **Package Management**:
    - [ ] Generate `requirements.txt` with pinned versions (`pandas_ta`, `yfinance`, `alpaca-trade-api`, `python-dotenv`, `requests`, `python-dotenv`).
3. **Robust Data Fetching**:
    - [ ] Add `try-except` blocks in `DataManager` methods.
    - [ ] Implement a simple retry decorator for network calls.

## Phase 2: Trading Engine Upgrades 📈
1. **Risk Management**:
    - [ ] Add `STOP_LOSS_PCT` and `TAKE_PROFIT_PCT` to `config.py`.
2. **Advanced Orders**:
    - [ ] Update `trader.py` to support Bracket Orders (entry + SL + TP).
3. **Dynamic Sizing**:
    - [ ] Implement `calculate_position_size()` in `trader.py` based on 2% of available equity.
4. **Market Awareness**:
    - [ ] Integrate `alpaca.get_clock()` to prevent trading when the market is closed.

## Phase 3: Analysis & Observability 🔍
1. **Indicator Expansion**:
    - [ ] Add MACD and Bollinger Bands to `PatternAnalyzer`.
2. **Telemetry**:
    - [ ] Implement structured JSON logging for each cycle.
3. **Multi-Symbol Support**:
    - [ ] Refactor `main.py` and `TradingBotLogic` to iterate through a `WATCHLIST` defined in `config.py`.

## Phase 4: Interface & CLI 💻
1. **CLI Integration**:
    - [ ] Add `argparse` to `main.py` for `--dry-run` and `--symbols` flags.
2. **GUI Enhancements**:
    - [ ] Add an "Emergency Stop" button to the Tkinter UI to close all positions.

---

## Technical Stack
- **Language**: Python 3.12+
- **APIs**: Alpaca (Trading), Alpha Vantage / yfinance (Data)
- **Libs**: `pandas`, `pandas_ta`, `alpaca-trade-api`, `python-dotenv`, `tkinter`
