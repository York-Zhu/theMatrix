"""
Spot data collection module for the crypto quantitative trading strategy.
Collects data for spot market factors from various sources.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import time

from src.utils.api_client import create_exchange_client
from src.utils.logger import setup_logger
from src.utils.config import (
    DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, DEFAULT_LIMIT
)

# Set up logger
logger = setup_logger("spot_data", "spot_data")

class SpotDataCollector:
    """Collector for spot market data."""
    
    def __init__(self, symbols: List[str] = None, timeframe: str = DEFAULT_TIMEFRAME,
                 limit: int = DEFAULT_LIMIT):
        """
        Initialize the spot data collector.
        
        Args:
            symbols (List[str], optional): List of symbols to collect data for. Defaults to DEFAULT_SYMBOLS.
            timeframe (str, optional): Time frame for data collection. Defaults to DEFAULT_TIMEFRAME.
            limit (int, optional): Number of data points to fetch. Defaults to DEFAULT_LIMIT.
        """
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.timeframe = timeframe
        self.limit = limit
        
        # Initialize exchange clients
        self.binance_client = create_exchange_client("binance")
        self.coinbase_client = create_exchange_client("coinbase")
        self.bitfinex_client = create_exchange_client("bitfinex")
        
    def get_ohlc_data(self, symbol: str) -> pd.DataFrame:
        """
        Get OHLC market data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: OHLC market data
        """
        try:
            logger.info(f"Fetching OHLC data for {symbol}")
            
            # Format symbol for exchange API
            formatted_symbol = f"{symbol}/USDT"
            
            # Get OHLCV data from Binance
            ohlcv = self.binance_client.get_ohlcv(formatted_symbol, self.timeframe, self.limit)
            
            if not ohlcv:
                logger.error(f"Failed to get OHLC data for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Add symbol column
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLC data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_orderbook_data(self, symbol: str) -> pd.DataFrame:
        """
        Get orderbook data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Orderbook data
        """
        try:
            logger.info(f"Fetching orderbook data for {symbol}")
            
            # Format symbol for exchange API
            formatted_symbol = f"{symbol}/USDT"
            
            # Get orderbook data from Binance
            orderbook = self.binance_client.get_orderbook(formatted_symbol)
            
            if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
                logger.error(f"Failed to get orderbook data for {symbol}")
                return pd.DataFrame()
            
            # Calculate orderbook metrics
            bids = orderbook['bids']
            asks = orderbook['asks']
            
            # Calculate bid-ask spread
            best_bid = bids[0][0] if bids else 0
            best_ask = asks[0][0] if asks else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0
            spread_pct = (spread / best_bid) * 100 if best_bid else 0
            
            # Calculate order book imbalance
            bid_volume = sum(bid[1] for bid in bids)
            ask_volume = sum(ask[1] for ask in asks)
            total_volume = bid_volume + ask_volume
            imbalance = (bid_volume - ask_volume) / total_volume if total_volume else 0
            
            # Calculate depth at different levels
            bid_depth_5pct = sum(bid[1] for bid in bids if bid[0] >= best_bid * 0.95)
            ask_depth_5pct = sum(ask[1] for ask in asks if ask[0] <= best_ask * 1.05)
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'symbol': [symbol],
                'best_bid': [best_bid],
                'best_ask': [best_ask],
                'spread': [spread],
                'spread_pct': [spread_pct],
                'bid_volume': [bid_volume],
                'ask_volume': [ask_volume],
                'imbalance': [imbalance],
                'bid_depth_5pct': [bid_depth_5pct],
                'ask_depth_5pct': [ask_depth_5pct]
            })
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching orderbook data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_coinbase_premium_index(self, symbol: str) -> pd.DataFrame:
        """
        Calculate Coinbase Premium Index for a symbol.
        
        Args:
            symbol (str): Symbol to calculate premium for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Coinbase Premium Index data
        """
        try:
            logger.info(f"Calculating Coinbase Premium Index for {symbol}")
            
            # Format symbol for exchange API
            formatted_symbol = f"{symbol}/USDT"
            coinbase_symbol = f"{symbol}/USD"
            
            # Get current price from Binance
            binance_orderbook = self.binance_client.get_orderbook(formatted_symbol)
            
            if not binance_orderbook or 'bids' not in binance_orderbook or 'asks' not in binance_orderbook:
                logger.error(f"Failed to get Binance price for {symbol}")
                return pd.DataFrame()
            
            binance_price = (binance_orderbook['bids'][0][0] + binance_orderbook['asks'][0][0]) / 2
            
            # Get current price from Coinbase
            coinbase_orderbook = self.coinbase_client.get_orderbook(coinbase_symbol)
            
            if not coinbase_orderbook or 'bids' not in coinbase_orderbook or 'asks' not in coinbase_orderbook:
                logger.error(f"Failed to get Coinbase price for {symbol}")
                return pd.DataFrame()
            
            coinbase_price = (coinbase_orderbook['bids'][0][0] + coinbase_orderbook['asks'][0][0]) / 2
            
            # Calculate premium
            premium = coinbase_price - binance_price
            premium_pct = (premium / binance_price) * 100
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'symbol': [symbol],
                'binance_price': [binance_price],
                'coinbase_price': [coinbase_price],
                'premium': [premium],
                'premium_pct': [premium_pct]
            })
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Coinbase Premium Index for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_bitfinex_margin_ratio(self, symbol: str) -> pd.DataFrame:
        """
        Get Bitfinex margin long/short ratio for a symbol.
        
        Args:
            symbol (str): Symbol to get ratio for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Bitfinex margin ratio data
        """
        try:
            logger.info(f"Fetching Bitfinex margin ratio for {symbol}")
            
            # Format symbol for Bitfinex API
            formatted_symbol = f"t{symbol}USD"
            
            # This is a placeholder as direct access to Bitfinex margin data
            # might require specific API endpoints not available in ccxt
            # In a real implementation, you would use the Bitfinex API directly
            
            # For demonstration purposes, we'll create a mock DataFrame
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'symbol': [symbol],
                'long_positions': [np.random.randint(1000, 5000)],
                'short_positions': [np.random.randint(1000, 5000)]
            })
            
            # Calculate long/short ratio
            df['long_short_ratio'] = df['long_positions'] / df['short_positions']
            
            logger.warning(f"Using mock data for Bitfinex margin ratio for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Bitfinex margin ratio for {symbol}: {e}")
            return pd.DataFrame()
    
    def collect_all_spot_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Collect all spot market data for a symbol.
        
        Args:
            symbol (str): Symbol to collect data for (e.g., "BTC")
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all spot market data
        """
        logger.info(f"Collecting all spot market data for {symbol}")
        
        # Collect data
        ohlc_df = self.get_ohlc_data(symbol)
        orderbook_df = self.get_orderbook_data(symbol)
        coinbase_premium_df = self.get_coinbase_premium_index(symbol)
        bitfinex_margin_df = self.get_bitfinex_margin_ratio(symbol)
        
        # Return all data
        return {
            'ohlc': ohlc_df,
            'orderbook': orderbook_df,
            'coinbase_premium': coinbase_premium_df,
            'bitfinex_margin_ratio': bitfinex_margin_df
        }
    
    def collect_data_for_all_symbols(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect spot market data for all symbols.
        
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: Dictionary containing spot market data for all symbols
        """
        logger.info(f"Collecting spot market data for all symbols: {self.symbols}")
        
        all_data = {}
        for symbol in self.symbols:
            all_data[symbol] = self.collect_all_spot_data(symbol)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        return all_data
