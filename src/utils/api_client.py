"""
API client module for the crypto quantitative trading strategy.
Provides functionality to interact with various cryptocurrency APIs.
"""
import time
import hmac
import hashlib
import json
import requests
from urllib.parse import urlencode
import ccxt
from typing import Dict, Any, Optional, List, Union

from src.utils.logger import setup_logger
from src.utils.config import (
    COINGLASS_API_KEY, BINANCE_API_KEY, BINANCE_API_SECRET,
    OKX_API_KEY, OKX_API_SECRET, BYBIT_API_KEY, BYBIT_API_SECRET,
    COINBASE_API_KEY, COINBASE_API_SECRET, BITFINEX_API_KEY, BITFINEX_API_SECRET,
    COINGLASS_BASE_URL
)

# Set up logger
logger = setup_logger("api_client", "api_client")

class APIClient:
    """Base API client class with common functionality."""
    
    def __init__(self, base_url: str, api_key: str = "", api_secret: str = ""):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for the API
            api_key (str, optional): API key for authentication. Defaults to "".
            api_secret (str, optional): API secret for authentication. Defaults to "".
        """
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and check for errors.
        
        Args:
            response (requests.Response): Response from the API
            
        Returns:
            Dict[str, Any]: Parsed JSON response
            
        Raises:
            Exception: If the API returns an error
        """
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint (str): API endpoint
            params (Dict[str, Any], optional): Query parameters. Defaults to None.
            
        Returns:
            Dict[str, Any]: Parsed JSON response
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
            
        response = self.session.get(url, params=params, headers=headers)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint (str): API endpoint
            data (Dict[str, Any]): Request data
            
        Returns:
            Dict[str, Any]: Parsed JSON response
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
            
        response = self.session.post(url, json=data, headers=headers)
        return self._handle_response(response)


class CoinglassClient(APIClient):
    """Client for interacting with the Coinglass API."""
    
    def __init__(self):
        """Initialize the Coinglass API client."""
        super().__init__(COINGLASS_BASE_URL, COINGLASS_API_KEY)
        
    def get_open_interest(self, symbol: str, exchange: Optional[str] = None, 
                         interval: str = "1h") -> Dict[str, Any]:
        """
        Get open interest data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            exchange (str, optional): Exchange to get data from. Defaults to None (all exchanges).
            interval (str, optional): Time interval. Defaults to "1h".
            
        Returns:
            Dict[str, Any]: Open interest data
        """
        params = {
            "symbol": symbol,
            "interval": interval
        }
        
        if exchange:
            params["exchange"] = exchange
            
        return self.get("/futures/openInterest", params)
    
    def get_funding_rate(self, symbol: str, exchange: Optional[str] = None) -> Dict[str, Any]:
        """
        Get funding rate data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            exchange (str, optional): Exchange to get data from. Defaults to None (all exchanges).
            
        Returns:
            Dict[str, Any]: Funding rate data
        """
        params = {"symbol": symbol}
        
        if exchange:
            params["exchange"] = exchange
            
        return self.get("/futures/fundingRate", params)
    
    def get_liquidation(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        """
        Get liquidation data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            timeframe (str, optional): Time frame. Defaults to "1h".
            
        Returns:
            Dict[str, Any]: Liquidation data
        """
        params = {
            "symbol": symbol,
            "timeframe": timeframe
        }
        
        return self.get("/futures/liquidation", params)


class ExchangeClient:
    """Client for interacting with cryptocurrency exchanges using CCXT."""
    
    def __init__(self, exchange_id: str, api_key: str = "", api_secret: str = ""):
        """
        Initialize the exchange client.
        
        Args:
            exchange_id (str): Exchange ID (e.g., "binance", "okx", "bybit")
            api_key (str, optional): API key for authentication. Defaults to "".
            api_secret (str, optional): API secret for authentication. Defaults to "".
        """
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Initialize CCXT exchange
        self.exchange = ccxt.exchange({
            'id': exchange_id,
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                 limit: int = 100) -> List[List[Union[int, float]]]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC/USDT")
            timeframe (str, optional): Time frame. Defaults to "1h".
            limit (int, optional): Number of data points to fetch. Defaults to 100.
            
        Returns:
            List[List[Union[int, float]]]: OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV data from {self.exchange_id}: {e}")
            return []
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get orderbook data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC/USDT")
            limit (int, optional): Depth of the orderbook. Defaults to 20.
            
        Returns:
            Dict[str, Any]: Orderbook data
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching orderbook data from {self.exchange_id}: {e}")
            return {"bids": [], "asks": []}


# Factory function to create exchange clients
def create_exchange_client(exchange_id: str) -> ExchangeClient:
    """
    Create an exchange client for the specified exchange.
    
    Args:
        exchange_id (str): Exchange ID (e.g., "binance", "okx", "bybit")
        
    Returns:
        ExchangeClient: Exchange client instance
    """
    if exchange_id.lower() == "binance":
        return ExchangeClient("binance", BINANCE_API_KEY, BINANCE_API_SECRET)
    elif exchange_id.lower() == "okx":
        return ExchangeClient("okx", OKX_API_KEY, OKX_API_SECRET)
    elif exchange_id.lower() == "bybit":
        return ExchangeClient("bybit", BYBIT_API_KEY, BYBIT_API_SECRET)
    elif exchange_id.lower() == "coinbase":
        return ExchangeClient("coinbase", COINBASE_API_KEY, COINBASE_API_SECRET)
    elif exchange_id.lower() == "bitfinex":
        return ExchangeClient("bitfinex", BITFINEX_API_KEY, BITFINEX_API_SECRET)
    else:
        raise ValueError(f"Unsupported exchange: {exchange_id}")
