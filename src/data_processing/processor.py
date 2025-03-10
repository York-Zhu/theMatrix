"""
Data processing module for the crypto quantitative trading strategy.
Processes and combines data from various sources for strategy calculations.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from src.utils.logger import setup_logger
from src.utils.config import (
    SHORT_WINDOW, MEDIUM_WINDOW, LONG_WINDOW,
    WEIGHTS
)

# Set up logger
logger = setup_logger("data_processor", "data_processor")

class DataProcessor:
    """Processor for market data."""
    
    def __init__(self):
        """Initialize the data processor."""
        pass
    
    def process_open_interest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process open interest data.
        
        Args:
            df (pd.DataFrame): Open interest data
            
        Returns:
            pd.DataFrame: Processed open interest data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for open interest processing")
            return df
        
        try:
            logger.info("Processing open interest data")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate change in open interest
            df['openInterest_change'] = df.groupby('exchange')['openInterest'].pct_change()
            df['openInterestUsd_change'] = df.groupby('exchange')['openInterestUsd'].pct_change()
            
            # Calculate rolling statistics
            for window in [SHORT_WINDOW, MEDIUM_WINDOW, LONG_WINDOW]:
                # Rolling mean
                df[f'openInterest_mean_{window}h'] = df.groupby('exchange')['openInterest'].transform(
                    lambda x: x.rolling(window=window).mean()
                )
                
                # Rolling standard deviation
                df[f'openInterest_std_{window}h'] = df.groupby('exchange')['openInterest'].transform(
                    lambda x: x.rolling(window=window).std()
                )
                
                # Z-score (how many standard deviations from the mean)
                df[f'openInterest_zscore_{window}h'] = (
                    (df['openInterest'] - df[f'openInterest_mean_{window}h']) / 
                    df[f'openInterest_std_{window}h']
                )
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing open interest data: {e}")
            return df
    
    def process_funding_rates(self, df: pd.DataFrame, open_interest_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process funding rate data and weight by open interest.
        
        Args:
            df (pd.DataFrame): Funding rate data
            open_interest_df (pd.DataFrame): Open interest data for weighting
            
        Returns:
            pd.DataFrame: Processed funding rate data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for funding rate processing")
            return df
        
        try:
            logger.info("Processing funding rate data")
            
            # If open interest data is available, weight funding rates by open interest
            if not open_interest_df.empty:
                # Get the latest open interest for each exchange
                latest_oi = open_interest_df.sort_values('timestamp').groupby('exchange').last().reset_index()
                latest_oi = latest_oi[['exchange', 'openInterestUsd']]
                
                # Merge with funding rate data
                df = pd.merge(df, latest_oi, on='exchange', how='left')
                
                # Calculate weighted funding rate
                total_oi = df['openInterestUsd'].sum()
                df['weight'] = df['openInterestUsd'] / total_oi if total_oi > 0 else 0
                df['weighted_funding_rate'] = df['funding_rate'] * df['weight']
                
                # Calculate aggregate weighted funding rate
                weighted_funding_rate = df['weighted_funding_rate'].sum()
                
                # Add to DataFrame
                df['aggregate_weighted_funding_rate'] = weighted_funding_rate
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing funding rate data: {e}")
            return df
    
    def process_orderbook_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process orderbook data.
        
        Args:
            df (pd.DataFrame): Orderbook data
            
        Returns:
            pd.DataFrame: Processed orderbook data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for orderbook processing")
            return df
        
        try:
            logger.info("Processing orderbook data")
            
            # Calculate additional metrics
            
            # Bid-ask ratio
            df['bid_ask_ratio'] = df['bid_volume'] / df['ask_volume']
            
            # Depth ratio
            df['depth_ratio'] = df['bid_depth_5pct'] / df['ask_depth_5pct']
            
            # Normalize imbalance to [-1, 1] range
            df['normalized_imbalance'] = df['imbalance'] * 2  # Already in [-0.5, 0.5] range
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing orderbook data: {e}")
            return df
    
    def process_rsi_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process RSI data.
        
        Args:
            df (pd.DataFrame): RSI data
            
        Returns:
            pd.DataFrame: Processed RSI data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for RSI processing")
            return df
        
        try:
            logger.info("Processing RSI data")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate RSI change
            df['rsi_change'] = df.groupby('exchange')['rsi'].diff()
            
            # Calculate RSI momentum (second derivative)
            df['rsi_momentum'] = df.groupby('exchange')['rsi_change'].diff()
            
            # Calculate RSI moving averages
            for window in [SHORT_WINDOW, MEDIUM_WINDOW]:
                df[f'rsi_ma_{window}h'] = df.groupby('exchange')['rsi'].transform(
                    lambda x: x.rolling(window=window).mean()
                )
            
            # Calculate RSI crossovers
            df['rsi_crossover'] = np.where(
                (df['rsi'] > df[f'rsi_ma_{SHORT_WINDOW}h']) & 
                (df['rsi'].shift(1) <= df[f'rsi_ma_{SHORT_WINDOW}h'].shift(1)),
                1,  # Bullish crossover
                np.where(
                    (df['rsi'] < df[f'rsi_ma_{SHORT_WINDOW}h']) & 
                    (df['rsi'].shift(1) >= df[f'rsi_ma_{SHORT_WINDOW}h'].shift(1)),
                    -1,  # Bearish crossover
                    0  # No crossover
                )
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing RSI data: {e}")
            return df
    
    def process_liquidation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process liquidation data.
        
        Args:
            df (pd.DataFrame): Liquidation data
            
        Returns:
            pd.DataFrame: Processed liquidation data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for liquidation processing")
            return df
        
        try:
            logger.info("Processing liquidation data")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate long/short liquidation ratio
            df['long_short_liquidation_ratio'] = df['longLiquidation'] / df['shortLiquidation'].replace(0, 1)
            
            # Calculate liquidation intensity (total liquidation / average)
            df['total_liquidation_ma'] = df['totalLiquidation'].rolling(window=24).mean()
            df['liquidation_intensity'] = df['totalLiquidation'] / df['total_liquidation_ma']
            
            # Calculate cumulative liquidations
            df['cumulative_long_liquidation'] = df['longLiquidation'].cumsum()
            df['cumulative_short_liquidation'] = df['shortLiquidation'].cumsum()
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing liquidation data: {e}")
            return df
    
    def process_coinbase_premium(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process Coinbase Premium Index data.
        
        Args:
            df (pd.DataFrame): Coinbase Premium Index data
            
        Returns:
            pd.DataFrame: Processed Coinbase Premium Index data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for Coinbase Premium processing")
            return df
        
        try:
            logger.info("Processing Coinbase Premium Index data")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate moving averages
            for window in [SHORT_WINDOW, MEDIUM_WINDOW]:
                df[f'premium_ma_{window}h'] = df['premium_pct'].rolling(window=window).mean()
            
            # Calculate z-score
            df['premium_std'] = df['premium_pct'].rolling(window=MEDIUM_WINDOW).std()
            df['premium_zscore'] = (df['premium_pct'] - df[f'premium_ma_{MEDIUM_WINDOW}h']) / df['premium_std']
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing Coinbase Premium Index data: {e}")
            return df
    
    def process_bitfinex_margin_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process Bitfinex margin long/short ratio data.
        
        Args:
            df (pd.DataFrame): Bitfinex margin ratio data
            
        Returns:
            pd.DataFrame: Processed Bitfinex margin ratio data
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for Bitfinex margin ratio processing")
            return df
        
        try:
            logger.info("Processing Bitfinex margin ratio data")
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate log of ratio (to center around 0)
            df['log_long_short_ratio'] = np.log(df['long_short_ratio'])
            
            # Calculate moving averages
            for window in [SHORT_WINDOW, MEDIUM_WINDOW]:
                df[f'ratio_ma_{window}h'] = df['long_short_ratio'].rolling(window=window).mean()
                df[f'log_ratio_ma_{window}h'] = df['log_long_short_ratio'].rolling(window=window).mean()
            
            # Calculate z-score
            df['log_ratio_std'] = df['log_long_short_ratio'].rolling(window=MEDIUM_WINDOW).std()
            df['ratio_zscore'] = (
                df['log_long_short_ratio'] - df[f'log_ratio_ma_{MEDIUM_WINDOW}h']
            ) / df['log_ratio_std']
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing Bitfinex margin ratio data: {e}")
            return df
    
    def process_futures_data(self, futures_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Process all futures market data.
        
        Args:
            futures_data (Dict[str, pd.DataFrame]): Dictionary containing futures market data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing processed futures market data
        """
        logger.info("Processing all futures market data")
        
        processed_data = {}
        
        # Process open interest data
        if 'open_interest' in futures_data and not futures_data['open_interest'].empty:
            processed_data['open_interest'] = self.process_open_interest(futures_data['open_interest'])
        
        # Process funding rates data
        if 'funding_rates' in futures_data and not futures_data['funding_rates'].empty:
            open_interest_df = futures_data.get('open_interest', pd.DataFrame())
            processed_data['funding_rates'] = self.process_funding_rates(
                futures_data['funding_rates'], open_interest_df
            )
        
        # Process orderbook data
        if 'orderbook' in futures_data and not futures_data['orderbook'].empty:
            processed_data['orderbook'] = self.process_orderbook_data(futures_data['orderbook'])
        
        # Process RSI data
        if 'rsi' in futures_data and not futures_data['rsi'].empty:
            processed_data['rsi'] = self.process_rsi_data(futures_data['rsi'])
        
        # Process liquidation data
        if 'liquidation' in futures_data and not futures_data['liquidation'].empty:
            processed_data['liquidation'] = self.process_liquidation_data(futures_data['liquidation'])
        
        return processed_data
    
    def process_spot_data(self, spot_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Process all spot market data.
        
        Args:
            spot_data (Dict[str, pd.DataFrame]): Dictionary containing spot market data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing processed spot market data
        """
        logger.info("Processing all spot market data")
        
        processed_data = {}
        
        # Process OHLC data
        if 'ohlc' in spot_data and not spot_data['ohlc'].empty:
            processed_data['ohlc'] = spot_data['ohlc']  # No additional processing needed
        
        # Process orderbook data
        if 'orderbook' in spot_data and not spot_data['orderbook'].empty:
            processed_data['orderbook'] = self.process_orderbook_data(spot_data['orderbook'])
        
        # Process Coinbase Premium Index data
        if 'coinbase_premium' in spot_data and not spot_data['coinbase_premium'].empty:
            processed_data['coinbase_premium'] = self.process_coinbase_premium(spot_data['coinbase_premium'])
        
        # Process Bitfinex margin ratio data
        if 'bitfinex_margin_ratio' in spot_data and not spot_data['bitfinex_margin_ratio'].empty:
            processed_data['bitfinex_margin_ratio'] = self.process_bitfinex_margin_ratio(
                spot_data['bitfinex_margin_ratio']
            )
        
        return processed_data
    
    def combine_processed_data(self, 
                              processed_futures_data: Dict[str, pd.DataFrame],
                              processed_spot_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Combine processed futures and spot market data into a single DataFrame.
        
        Args:
            processed_futures_data (Dict[str, pd.DataFrame]): Dictionary containing processed futures market data
            processed_spot_data (Dict[str, pd.DataFrame]): Dictionary containing processed spot market data
            
        Returns:
            pd.DataFrame: Combined data for strategy calculations
        """
        logger.info("Combining processed futures and spot market data")
        
        # Extract the latest data points from each DataFrame
        combined_data = {}
        
        # Process futures data
        for key, df in processed_futures_data.items():
            if df.empty:
                continue
                
            if key == 'open_interest':
                # Get the latest open interest change
                latest = df.sort_values('timestamp').groupby('exchange').last().reset_index()
                combined_data['open_interest_change'] = latest['openInterestUsd_change'].mean()
                
                # Get the latest z-score
                combined_data['open_interest_zscore'] = latest[f'openInterest_zscore_{MEDIUM_WINDOW}h'].mean()
                
            elif key == 'funding_rates':
                # Get the aggregate weighted funding rate
                if 'aggregate_weighted_funding_rate' in df.columns:
                    combined_data['weighted_funding_rate'] = df['aggregate_weighted_funding_rate'].iloc[0]
                else:
                    combined_data['funding_rate'] = df['funding_rate'].mean()
                    
            elif key == 'orderbook':
                # Get the average imbalance
                combined_data['orderbook_imbalance'] = df['normalized_imbalance'].mean()
                
                # Get the average bid-ask ratio
                combined_data['bid_ask_ratio'] = df['bid_ask_ratio'].mean()
                
            elif key == 'rsi':
                # Get the latest RSI
                latest = df.sort_values('timestamp').groupby('exchange').last().reset_index()
                combined_data['rsi'] = latest['rsi'].mean()
                
                # Get the latest RSI crossover
                combined_data['rsi_crossover'] = latest['rsi_crossover'].mean()
                
            elif key == 'liquidation':
                # Get the latest liquidation intensity
                latest = df.sort_values('timestamp').last()
                combined_data['liquidation_intensity'] = latest['liquidation_intensity']
                
                # Get the latest long/short liquidation ratio
                combined_data['long_short_liquidation_ratio'] = latest['long_short_liquidation_ratio']
        
        # Process spot data
        for key, df in processed_spot_data.items():
            if df.empty:
                continue
                
            if key == 'coinbase_premium':
                # Get the latest premium
                latest = df.sort_values('timestamp').last()
                combined_data['coinbase_premium'] = latest['premium_pct']
                
                # Get the latest premium z-score
                if 'premium_zscore' in latest:
                    combined_data['coinbase_premium_zscore'] = latest['premium_zscore']
                    
            elif key == 'bitfinex_margin_ratio':
                # Get the latest ratio
                latest = df.sort_values('timestamp').last()
                combined_data['bitfinex_margin_ratio'] = latest['long_short_ratio']
                
                # Get the latest ratio z-score
                if 'ratio_zscore' in latest:
                    combined_data['bitfinex_margin_ratio_zscore'] = latest['ratio_zscore']
        
        # Create DataFrame
        combined_df = pd.DataFrame([combined_data])
        
        # Add timestamp
        combined_df['timestamp'] = datetime.now()
        
        return combined_df
