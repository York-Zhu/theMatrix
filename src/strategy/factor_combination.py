"""
Factor combination module for the crypto quantitative trading strategy.
Combines multiple factors to generate trading signals.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union

from src.utils.logger import setup_logger
from src.utils.config import WEIGHTS

# Set up logger
logger = setup_logger("factor_combination", "factor_combination")

class FactorCombination:
    """Combines multiple factors for trading signals."""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the factor combination.
        
        Args:
            weights (Dict[str, float], optional): Weights for each factor. Defaults to None.
        """
        self.weights = weights or WEIGHTS
        
        # Normalize weights to sum to 1
        total_weight = sum(self.weights.values())
        if total_weight != 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
    def combine_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Combine multiple factors into a single signal.
        
        Args:
            data (pd.DataFrame): Data containing factor values
            
        Returns:
            pd.DataFrame: Data with combined signal
        """
        if data.empty:
            logger.warning("Empty DataFrame provided for factor combination")
            return data
        
        try:
            logger.info("Combining factors")
            
            # Make a copy of the DataFrame
            result_df = data.copy()
            
            # Initialize combined signal
            result_df['combined_signal'] = 0.0
            
            # Add weighted contribution from each factor
            for factor, weight in self.weights.items():
                if factor in data.columns:
                    result_df['combined_signal'] += data[factor] * weight
                elif f'{factor}_normalized' in data.columns:
                    result_df['combined_signal'] += data[f'{factor}_normalized'] * weight
                else:
                    logger.warning(f"Factor {factor} not found in data")
            
            # Classify signal
            result_df['signal'] = np.where(
                result_df['combined_signal'] > 0.2,
                1,  # Buy signal
                np.where(
                    result_df['combined_signal'] < -0.2,
                    -1,  # Sell signal
                    0  # Neutral
                )
            )
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error combining factors: {e}")
            return data
    
    def optimize_weights(self, historical_data: pd.DataFrame, target_column: str) -> Dict[str, float]:
        """
        Optimize factor weights based on historical performance.
        
        Args:
            historical_data (pd.DataFrame): Historical data with factor values and target
            target_column (str): Column name for the target variable
            
        Returns:
            Dict[str, float]: Optimized weights
        """
        if historical_data.empty:
            logger.warning("Empty DataFrame provided for weight optimization")
            return self.weights
        
        try:
            logger.info("Optimizing factor weights")
            
            # This is a placeholder for weight optimization
            # In a real implementation, you would use techniques like:
            # - Linear regression
            # - Genetic algorithms
            # - Bayesian optimization
            # - Grid search
            
            # For now, we'll just calculate correlation with the target
            correlations = {}
            
            for factor in self.weights.keys():
                if factor in historical_data.columns and target_column in historical_data.columns:
                    corr = historical_data[factor].corr(historical_data[target_column])
                    correlations[factor] = abs(corr)
                elif f'{factor}_normalized' in historical_data.columns and target_column in historical_data.columns:
                    corr = historical_data[f'{factor}_normalized'].corr(historical_data[target_column])
                    correlations[factor] = abs(corr)
            
            # Normalize correlations to sum to 1
            total_corr = sum(correlations.values())
            if total_corr != 0:
                optimized_weights = {k: v / total_corr for k, v in correlations.items()}
                
                # Update weights that were found in the data
                for factor in self.weights.keys():
                    if factor in optimized_weights:
                        self.weights[factor] = optimized_weights[factor]
            
            logger.info(f"Optimized weights: {self.weights}")
            
            return self.weights
            
        except Exception as e:
            logger.error(f"Error optimizing weights: {e}")
            return self.weights
