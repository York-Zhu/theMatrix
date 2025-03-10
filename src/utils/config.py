"""
Configuration module for the crypto quantitative trading strategy.
Contains settings for API endpoints, authentication, and strategy parameters.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Authentication
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY", "")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_API_SECRET = os.getenv("OKX_API_SECRET", "")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET", "")
BITFINEX_API_KEY = os.getenv("BITFINEX_API_KEY", "")
BITFINEX_API_SECRET = os.getenv("BITFINEX_API_SECRET", "")

# API Endpoints
# Coinglass API endpoints
COINGLASS_BASE_URL = "https://open-api.coinglass.com/api/pro/v1"
COINGLASS_OPEN_INTEREST_ENDPOINT = f"{COINGLASS_BASE_URL}/futures/openInterest"
COINGLASS_FUNDING_RATE_ENDPOINT = f"{COINGLASS_BASE_URL}/futures/fundingRate"
COINGLASS_LIQUIDATION_ENDPOINT = f"{COINGLASS_BASE_URL}/futures/liquidation"

# Exchange API endpoints
BINANCE_BASE_URL = "https://api.binance.com"
OKX_BASE_URL = "https://www.okx.com"
BYBIT_BASE_URL = "https://api.bybit.com"
COINBASE_BASE_URL = "https://api.coinbase.com"
BITFINEX_BASE_URL = "https://api.bitfinex.com"

# Data Collection Parameters
DEFAULT_SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
DEFAULT_TIMEFRAME = "1h"  # 1h, 4h, 1d
DEFAULT_LIMIT = 100  # Number of data points to fetch
DEFAULT_EXCHANGES = ["Binance", "OKX", "Bybit"]

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
FUNDING_RATE_THRESHOLD = 0.01  # 1% threshold for funding rate signals
OPEN_INTEREST_CHANGE_THRESHOLD = 0.05  # 5% threshold for open interest change signals
COINBASE_PREMIUM_THRESHOLD = 0.005  # 0.5% threshold for Coinbase premium signals
BITFINEX_MARGIN_RATIO_THRESHOLD = 1.5  # Threshold for long/short ratio signals

# Time Windows for Data Aggregation
SHORT_WINDOW = 12  # 12 hours
MEDIUM_WINDOW = 24  # 24 hours
LONG_WINDOW = 72  # 72 hours

# Factor Weights for Combination
WEIGHTS = {
    "open_interest": 0.2,
    "funding_rate": 0.2,
    "orderbook_imbalance": 0.15,
    "rsi": 0.15,
    "coinbase_premium": 0.15,
    "bitfinex_margin_ratio": 0.15,
}

# Backtesting Parameters
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2023-12-31"
TRANSACTION_FEE = 0.001  # 0.1% fee per trade
INITIAL_CAPITAL = 10000  # Initial capital for backtesting
