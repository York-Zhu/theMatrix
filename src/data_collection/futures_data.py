"""
Futures data collection module for the crypto quantitative trading strategy.
Collects data for futures market factors from various sources.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import time
from ta.momentum import RSIIndicator

from src.utils.api_client import CoinglassClient, create_exchange_client
from src.utils.logger import setup_logger
from src.utils.config import (
    DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, DEFAULT_LIMIT, DEFAULT_EXCHANGES,
    RSI_PERIOD
)

# Set up logger
logger = setup_logger("futures_data", "futures_data")

class FuturesDataCollector:
    """Collector for futures market data."""
    
    def __init__(self, symbols: List[str] = None, timeframe: str = DEFAULT_TIMEFRAME,
                 limit: int = DEFAULT_LIMIT, exchanges: List[str] = None):
        """
        Initialize the futures data collector.
        
        Args:
            symbols (List[str], optional): List of symbols to collect data for. Defaults to DEFAULT_SYMBOLS.
            timeframe (str, optional): Time frame for data collection. Defaults to DEFAULT_TIMEFRAME.
            limit (int, optional): Number of data points to fetch. Defaults to DEFAULT_LIMIT.
            exchanges (List[str], optional): List of exchanges to collect data from. Defaults to DEFAULT_EXCHANGES.
        """
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.timeframe = timeframe
        self.limit = limit
        self.exchanges = exchanges or DEFAULT_EXCHANGES
        
        # Initialize clients
        self.coinglass_client = CoinglassClient()
        self.exchange_clients = {
            exchange: create_exchange_client(exchange)
            for exchange in self.exchanges
        }
        
    def get_open_interest(self, symbol: str) -> pd.DataFrame:
        """
        Get open interest data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Open interest data
        """
        try:
            logger.info(f"Fetching open interest data for {symbol}")
            response = self.coinglass_client.get_open_interest(symbol, interval=self.timeframe)
            
            if not response or 'data' not in response:
                logger.error(f"Failed to get open interest data for {symbol}")
                return pd.DataFrame()
            
            # Extract and process data
            data = response['data']
            
            # Create DataFrame
            df_list = []
            for exchange_data in data:
                exchange_name = exchange_data.get('exchangeName', 'Unknown')
                if exchange_name not in self.exchanges:
                    continue
                
                history = exchange_data.get('dataMap', {}).get(symbol, [])
                if not history:
                    continue
                
                df = pd.DataFrame(history)
                df['exchange'] = exchange_name
                df_list.append(df)
            
            if not df_list:
                logger.warning(f"No open interest data found for {symbol}")
                return pd.DataFrame()
            
            # Combine data from all exchanges
            df_combined = pd.concat(df_list, ignore_index=True)
            
            # Convert timestamp to datetime
            df_combined['timestamp'] = pd.to_datetime(df_combined['createTime'], unit='ms')
            
            # Select relevant columns
            df_combined = df_combined[['timestamp', 'exchange', 'openInterest', 'openInterestUsd']]
            
            return df_combined
            
        except Exception as e:
            logger.error(f"Error fetching open interest data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_funding_rates(self, symbol: str) -> pd.DataFrame:
        """
        Get funding rate data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Funding rate data
        """
        try:
            logger.info(f"Fetching funding rate data for {symbol}")
            response = self.coinglass_client.get_funding_rate(symbol)
            
            if not response or 'data' not in response:
                logger.error(f"Failed to get funding rate data for {symbol}")
                return pd.DataFrame()
            
            # Extract and process data
            data = response['data']
            
            # Create DataFrame
            df_list = []
            for exchange_data in data:
                exchange_name = exchange_data.get('exchangeName', 'Unknown')
                if exchange_name not in self.exchanges:
                    continue
                
                funding_rate = exchange_data.get('rate', 0)
                next_funding_time = exchange_data.get('nextFundingTime', 0)
                
                df = pd.DataFrame({
                    'exchange': [exchange_name],
                    'funding_rate': [funding_rate],
                    'next_funding_time': [next_funding_time]
                })
                df_list.append(df)
            
            if not df_list:
                logger.warning(f"No funding rate data found for {symbol}")
                return pd.DataFrame()
            
            # Combine data from all exchanges
            df_combined = pd.concat(df_list, ignore_index=True)
            
            # Convert timestamp to datetime
            df_combined['next_funding_time'] = pd.to_datetime(df_combined['next_funding_time'], unit='ms')
            
            # Add symbol column
            df_combined['symbol'] = symbol
            
            return df_combined
            
        except Exception as e:
            logger.error(f"Error fetching funding rate data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_orderbook_data(self, symbol: str) -> pd.DataFrame:
        """
        Get aggregated orderbook data for a symbol from multiple exchanges.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Aggregated orderbook data
        """
        try:
            logger.info(f"Fetching orderbook data for {symbol}")
            
            # Format symbol for exchange API
            formatted_symbol = f"{symbol}/USDT"
            
            # Collect orderbook data from each exchange
            orderbook_data = []
            for exchange_name, client in self.exchange_clients.items():
                try:
                    orderbook = client.get_orderbook(formatted_symbol)
                    
                    if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
                        logger.warning(f"No orderbook data found for {symbol} on {exchange_name}")
                        continue
                    
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
                    
                    orderbook_data.append({
                        'timestamp': datetime.now(),
                        'exchange': exchange_name,
                        'symbol': symbol,
                        'best_bid': best_bid,
                        'best_ask': best_ask,
                        'spread': spread,
                        'spread_pct': spread_pct,
                        'bid_volume': bid_volume,
                        'ask_volume': ask_volume,
                        'imbalance': imbalance,
                        'bid_depth_5pct': bid_depth_5pct,
                        'ask_depth_5pct': ask_depth_5pct
                    })
                    
                except Exception as e:
                    logger.error(f"Error fetching orderbook data for {symbol} on {exchange_name}: {e}")
                    continue
            
            if not orderbook_data:
                logger.warning(f"No orderbook data collected for {symbol}")
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(orderbook_data)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching orderbook data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, symbol: str) -> pd.DataFrame:
        """
        Calculate RSI technical indicator for a symbol.
        
        Args:
            symbol (str): Symbol to calculate RSI for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: RSI data
        """
        try:
            logger.info(f"Calculating RSI for {symbol}")
            
            # Format symbol for exchange API
            formatted_symbol = f"{symbol}/USDT"
            
            # Collect OHLCV data from each exchange
            rsi_data = []
            for exchange_name, client in self.exchange_clients.items():
                try:
                    ohlcv = client.get_ohlcv(formatted_symbol, self.timeframe, self.limit)
                    
                    if not ohlcv:
                        logger.warning(f"No OHLCV data found for {symbol} on {exchange_name}")
                        continue
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Calculate RSI
                    rsi_indicator = RSIIndicator(close=df['close'], window=RSI_PERIOD)
                    df['rsi'] = rsi_indicator.rsi()
                    
                    # Add exchange and symbol columns
                    df['exchange'] = exchange_name
                    df['symbol'] = symbol
                    
                    # Select relevant columns
                    df = df[['timestamp', 'exchange', 'symbol', 'close', 'rsi']]
                    
                    rsi_data.append(df)
                    
                except Exception as e:
                    logger.error(f"Error calculating RSI for {symbol} on {exchange_name}: {e}")
                    continue
            
            if not rsi_data:
                logger.warning(f"No RSI data calculated for {symbol}")
                return pd.DataFrame()
            
            # Combine data from all exchanges
            df_combined = pd.concat(rsi_data, ignore_index=True)
            
            return df_combined
            
        except Exception as e:
            logger.error(f"Error calculating RSI for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_liquidation_data(self, symbol: str) -> pd.DataFrame:
        """
        Get liquidation data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for (e.g., "BTC")
            
        Returns:
            pd.DataFrame: Liquidation data
        """
        try:
            logger.info(f"Fetching liquidation data for {symbol}")
            
            # Check if API key is available
            if not self.coinglass_client.api_key:
                logger.warning("Coinglass API key not available for liquidation data")
                return pd.DataFrame()
            
            response = self.coinglass_client.get_liquidation(symbol, timeframe=self.timeframe)
            
            if not response or 'data' not in response:
                logger.error(f"Failed to get liquidation data for {symbol}")
                return pd.DataFrame()
            
            # Extract and process data
            data = response['data']
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['createTime'], unit='ms')
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Select relevant columns
            df = df[['timestamp', 'symbol', 'longLiquidation', 'shortLiquidation', 'totalLiquidation']]
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching liquidation data for {symbol}: {e}")
            return pd.DataFrame()
    
    def collect_all_futures_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Collect all futures market data for a symbol.
        
        Args:
            symbol (str): Symbol to collect data for (e.g., "BTC")
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all futures market data
        """
        logger.info(f"Collecting all futures market data for {symbol}")
        
        # Collect data
        open_interest_df = self.get_open_interest(symbol)
        funding_rates_df = self.get_funding_rates(symbol)
        orderbook_df = self.get_orderbook_data(symbol)
        rsi_df = self.calculate_rsi(symbol)
        liquidation_df = self.get_liquidation_data(symbol)
        
        # Return all data
        return {
            'open_interest': open_interest_df,
            'funding_rates': funding_rates_df,
            'orderbook': orderbook_df,
            'rsi': rsi_df,
            'liquidation': liquidation_df
        }
    
    def collect_data_for_all_symbols(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect futures market data for all symbols.
        
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: Dictionary containing futures market data for all symbols
        """
        logger.info(f"Collecting futures market data for all symbols: {self.symbols}")
        
        all_data = {}
        for symbol in self.symbols:
            all_data[symbol] = self.collect_all_futures_data(symbol)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        return all_data
