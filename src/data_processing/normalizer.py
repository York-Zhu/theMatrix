"""
Data normalization module for the crypto quantitative trading strategy.
Normalizes data from various sources for consistent strategy calculations.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger("data_normalizer", "data_normalizer")

class DataNormalizer:
    """Normalizer for market data."""
    
    def __init__(self, normalization_method: str = 'z-score'):
        """
        Initialize the data normalizer.
        
        Args:
            normalization_method (str, optional): Method for normalization. 
                Options: 'z-score', 'min-max'. Defaults to 'z-score'.
        """
        self.normalization_method = normalization_method
        self.scalers = {}
        
    def normalize_feature(self, feature_name: str, data: np.ndarray) -> np.ndarray:
        """
        Normalize a feature using the specified method.
        
        Args:
            feature_name (str): Name of the feature
            data (np.ndarray): Data to normalize
            
        Returns:
            np.ndarray: Normalized data
        """
        try:
            logger.info(f"Normalizing feature: {feature_name}")
            
            # Handle NaN values
            data = np.nan_to_num(data, nan=0.0)
            
            # Reshape data for scikit-learn
            data_reshaped = data.reshape(-1, 1)
            
            if self.normalization_method == 'z-score':
                # Initialize scaler if not exists
                if feature_name not in self.scalers:
                    self.scalers[feature_name] = StandardScaler()
                    self.scalers[feature_name].fit(data_reshaped)
                
                # Transform data
                normalized_data = self.scalers[feature_name].transform(data_reshaped).flatten()
                
            elif self.normalization_method == 'min-max':
                # Initialize scaler if not exists
                if feature_name not in self.scalers:
                    self.scalers[feature_name] = MinMaxScaler(feature_range=(-1, 1))
                    self.scalers[feature_name].fit(data_reshaped)
                
                # Transform data
                normalized_data = self.scalers[feature_name].transform(data_reshaped).flatten()
                
            else:
                logger.warning(f"Unknown normalization method: {self.normalization_method}. Using raw data.")
                normalized_data = data
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing feature {feature_name}: {e}")
            return data
    
    def normalize_dataframe(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        Normalize specified columns in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to normalize
            columns (List[str], optional): Columns to normalize. If None, all numeric columns will be normalized.
            
        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for normalization")
            return df
        
        try:
            logger.info("Normalizing DataFrame")
            
            # Make a copy of the DataFrame
            normalized_df = df.copy()
            
            # If columns not specified, use all numeric columns
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Normalize each column
            for column in columns:
                if column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
                    normalized_df[f'{column}_normalized'] = self.normalize_feature(column, df[column].values)
            
            return normalized_df
            
        except Exception as e:
            logger.error(f"Error normalizing DataFrame: {e}")
            return df
    
    def fit_scalers(self, df: pd.DataFrame, columns: List[str] = None) -> None:
        """
        Fit scalers on historical data.
        
        Args:
            df (pd.DataFrame): Historical data
            columns (List[str], optional): Columns to fit scalers for. If None, all numeric columns will be used.
        """
        if df.empty:
            logger.warning("Empty DataFrame provided for fitting scalers")
            return
        
        try:
            logger.info("Fitting scalers on historical data")
            
            # If columns not specified, use all numeric columns
            if columns is None:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Fit scaler for each column
            for column in columns:
                if column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
                    data = np.nan_to_num(df[column].values, nan=0.0).reshape(-1, 1)
                    
                    if self.normalization_method == 'z-score':
                        self.scalers[column] = StandardScaler()
                        self.scalers[column].fit(data)
                        
                    elif self.normalization_method == 'min-max':
                        self.scalers[column] = MinMaxScaler(feature_range=(-1, 1))
                        self.scalers[column].fit(data)
            
            logger.info(f"Fitted scalers for {len(self.scalers)} features")
            
        except Exception as e:
            logger.error(f"Error fitting scalers: {e}")
    
    def reset_scalers(self) -> None:
        """Reset all scalers."""
        self.scalers = {}
        logger.info("All scalers have been reset")
