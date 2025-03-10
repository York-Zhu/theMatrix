"""
Signal generator module for the crypto quantitative trading strategy.
Generates trading signals based on combined factors.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.utils.logger import setup_logger
from src.utils.config import (
    FUNDING_RATE_THRESHOLD,
    OPEN_INTEREST_CHANGE_THRESHOLD,
    COINBASE_PREMIUM_THRESHOLD,
    BITFINEX_MARGIN_RATIO_THRESHOLD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD
)
from src.strategy.factor_combination import FactorCombination

# Set up logger
logger = setup_logger("signal_generator", "signal_generator")

class SignalGenerator:
    """Generates trading signals based on market data."""
    
    def __init__(self, factor_combiner: FactorCombination = None):
        """
        Initialize the signal generator.
        
        Args:
            factor_combiner (FactorCombination, optional): Factor combination instance. Defaults to None.
        """
        self.factor_combiner = factor_combiner or FactorCombination()
        
    def generate_individual_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate individual signals for each factor.
        
        Args:
            data (pd.DataFrame): Data containing factor values
            
        Returns:
            pd.DataFrame: Data with individual signals
        """
        if data.empty:
            logger.warning("Empty DataFrame provided for signal generation")
            return data
        
        try:
            logger.info("Generating individual signals")
            
            # Make a copy of the DataFrame
            result_df = data.copy()
            
            # Generate signals for each factor
            
            # Open Interest signal
            if 'open_interest_change' in data.columns:
                result_df['open_interest_signal'] = np.where(
                    data['open_interest_change'] > OPEN_INTEREST_CHANGE_THRESHOLD,
                    1,  # Bullish signal
                    np.where(
                        data['open_interest_change'] < -OPEN_INTEREST_CHANGE_THRESHOLD,
                        -1,  # Bearish signal
                        0  # Neutral
                    )
                )
            
            # Funding Rate signal
            if 'weighted_funding_rate' in data.columns:
                result_df['funding_rate_signal'] = np.where(
                    data['weighted_funding_rate'] < -FUNDING_RATE_THRESHOLD,
                    1,  # Bullish signal (negative funding rate)
                    np.where(
                        data['weighted_funding_rate'] > FUNDING_RATE_THRESHOLD,
                        -1,  # Bearish signal (positive funding rate)
                        0  # Neutral
                    )
                )
            elif 'funding_rate' in data.columns:
                result_df['funding_rate_signal'] = np.where(
                    data['funding_rate'] < -FUNDING_RATE_THRESHOLD,
                    1,  # Bullish signal (negative funding rate)
                    np.where(
                        data['funding_rate'] > FUNDING_RATE_THRESHOLD,
                        -1,  # Bearish signal (positive funding rate)
                        0  # Neutral
                    )
                )
            
            # Orderbook Imbalance signal
            if 'orderbook_imbalance' in data.columns:
                result_df['orderbook_imbalance_signal'] = np.where(
                    data['orderbook_imbalance'] > 0.2,
                    1,  # Bullish signal (more bids than asks)
                    np.where(
                        data['orderbook_imbalance'] < -0.2,
                        -1,  # Bearish signal (more asks than bids)
                        0  # Neutral
                    )
                )
            
            # RSI signal
            if 'rsi' in data.columns:
                result_df['rsi_signal'] = np.where(
                    data['rsi'] < RSI_OVERSOLD,
                    1,  # Bullish signal (oversold)
                    np.where(
                        data['rsi'] > RSI_OVERBOUGHT,
                        -1,  # Bearish signal (overbought)
                        0  # Neutral
                    )
                )
            
            # Coinbase Premium signal
            if 'coinbase_premium' in data.columns:
                result_df['coinbase_premium_signal'] = np.where(
                    data['coinbase_premium'] > COINBASE_PREMIUM_THRESHOLD,
                    1,  # Bullish signal (premium is positive)
                    np.where(
                        data['coinbase_premium'] < -COINBASE_PREMIUM_THRESHOLD,
                        -1,  # Bearish signal (premium is negative)
                        0  # Neutral
                    )
                )
            
            # Bitfinex Margin Ratio signal
            if 'bitfinex_margin_ratio' in data.columns:
                result_df['bitfinex_margin_ratio_signal'] = np.where(
                    data['bitfinex_margin_ratio'] > BITFINEX_MARGIN_RATIO_THRESHOLD,
                    1,  # Bullish signal (more longs than shorts)
                    np.where(
                        data['bitfinex_margin_ratio'] < 1/BITFINEX_MARGIN_RATIO_THRESHOLD,
                        -1,  # Bearish signal (more shorts than longs)
                        0  # Neutral
                    )
                )
            
            # Liquidation signal
            if 'liquidation_intensity' in data.columns and 'long_short_liquidation_ratio' in data.columns:
                # High liquidation intensity with more shorts being liquidated is bullish
                result_df['liquidation_signal'] = np.where(
                    (data['liquidation_intensity'] > 1.5) & (data['long_short_liquidation_ratio'] < 0.8),
                    1,  # Bullish signal
                    np.where(
                        (data['liquidation_intensity'] > 1.5) & (data['long_short_liquidation_ratio'] > 1.2),
                        -1,  # Bearish signal
                        0  # Neutral
                    )
                )
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error generating individual signals: {e}")
            return data
    
    def generate_combined_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate combined signal from individual factor signals.
        
        Args:
            data (pd.DataFrame): Data containing individual factor signals
            
        Returns:
            pd.DataFrame: Data with combined signal
        """
        if data.empty:
            logger.warning("Empty DataFrame provided for combined signal generation")
            return data
        
        try:
            logger.info("Generating combined signal")
            
            # Generate individual signals if not already present
            if not any(col.endswith('_signal') for col in data.columns):
                data = self.generate_individual_signals(data)
            
            # Use factor combiner to generate combined signal
            result_df = self.factor_combiner.combine_factors(data)
            
            # Add timestamp
            result_df['signal_timestamp'] = datetime.now()
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error generating combined signal: {e}")
            return data
    
    def backtest_signals(self, historical_data: pd.DataFrame, price_column: str = 'close') -> pd.DataFrame:
        """
        Backtest signals on historical data.
        
        Args:
            historical_data (pd.DataFrame): Historical data with factor values and price
            price_column (str, optional): Column name for the price. Defaults to 'close'.
            
        Returns:
            pd.DataFrame: Backtest results
        """
        if historical_data.empty:
            logger.warning("Empty DataFrame provided for backtesting")
            return pd.DataFrame()
        
        try:
            logger.info("Backtesting signals")
            
            # Make a copy of the DataFrame
            result_df = historical_data.copy()
            
            # Generate signals
            result_df = self.generate_combined_signal(result_df)
            
            # Calculate returns
            result_df['next_return'] = result_df[price_column].pct_change(1).shift(-1)
            
            # Calculate strategy returns
            result_df['strategy_return'] = result_df['signal'] * result_df['next_return']
            
            # Calculate cumulative returns
            result_df['cumulative_market_return'] = (1 + result_df['next_return']).cumprod() - 1
            result_df['cumulative_strategy_return'] = (1 + result_df['strategy_return']).cumprod() - 1
            
            # Calculate performance metrics
            total_trades = (result_df['signal'] != 0).sum()
            winning_trades = (result_df['strategy_return'] > 0).sum()
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            avg_win = result_df.loc[result_df['strategy_return'] > 0, 'strategy_return'].mean()
            avg_loss = result_df.loc[result_df['strategy_return'] < 0, 'strategy_return'].mean()
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            # Add performance metrics to the DataFrame
            result_df.attrs['total_trades'] = total_trades
            result_df.attrs['winning_trades'] = winning_trades
            result_df.attrs['win_rate'] = win_rate
            result_df.attrs['profit_factor'] = profit_factor
            
            logger.info(f"Backtest results: Win Rate = {win_rate:.2%}, Profit Factor = {profit_factor:.2f}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error backtesting signals: {e}")
            return pd.DataFrame()
