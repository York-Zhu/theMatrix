"""
Data processing script for the crypto quantitative trading strategy.
Provides functionality for data cleaning, backtesting, and correlation analysis.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
import argparse
import os
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from src.data_collection.futures_data import FuturesDataCollector
from src.data_collection.spot_data import SpotDataCollector
from src.data_processing.processor import DataProcessor
from src.data_processing.normalizer import DataNormalizer
from src.strategy.factor_combination import FactorCombination
from src.strategy.signal_generator import SignalGenerator
from src.utils.logger import setup_logger
from src.utils.config import (
    DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, DEFAULT_LIMIT, DEFAULT_EXCHANGES,
    WEIGHTS, BACKTEST_START_DATE, BACKTEST_END_DATE, INITIAL_CAPITAL, TRANSACTION_FEE
)

# Set up logger
logger = setup_logger("data_processing_script", "data_processing_script")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Data Processing Script for Crypto Quantitative Trading Strategy')
    
    parser.add_argument('--input', default='data',
                        help='Input directory for data files')
    parser.add_argument('--output', default='results',
                        help='Output directory for results')
    parser.add_argument('--symbols', nargs='+', default=DEFAULT_SYMBOLS,
                        help='Symbols to process')
    parser.add_argument('--start-date', default=BACKTEST_START_DATE,
                        help='Start date for backtesting (YYYY-MM-DD)')
    parser.add_argument('--end-date', default=BACKTEST_END_DATE,
                        help='End date for backtesting (YYYY-MM-DD)')
    parser.add_argument('--mode', choices=['clean', 'backtest', 'correlation', 'factor_analysis', 'all'],
                        default='all', help='Mode of operation')
    
    return parser.parse_args()

def load_data(args):
    """
    Load data from files.
    
    Args:
        args: Command line arguments
        
    Returns:
        Dict: Loaded data
    """
    logger.info("Loading data from files")
    
    # Check if input directory exists
    if not os.path.exists(args.input):
        logger.error(f"Input directory {args.input} does not exist")
        return {}
    
    # Load data for each symbol
    data = {}
    
    for symbol in args.symbols:
        logger.info(f"Loading data for {symbol}")
        
        # Find latest files for the symbol
        symbol_files = [f for f in os.listdir(args.input) if f.startswith(symbol)]
        
        if not symbol_files:
            logger.warning(f"No files found for {symbol}")
            continue
        
        # Group files by type
        futures_files = [f for f in symbol_files if 'futures' in f]
        spot_files = [f for f in symbol_files if 'spot' in f]
        processed_files = [f for f in symbol_files if 'combined' in f or 'normalized' in f]
        signal_files = [f for f in symbol_files if 'signals' in f]
        
        # Load data
        symbol_data = {
            'futures_data': {},
            'spot_data': {},
            'processed_data': {},
            'signals': {}
        }
        
        # Load futures data
        for file in futures_files:
            key = file.split('_')[2]  # Extract key from filename
            file_path = os.path.join(args.input, file)
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            symbol_data['futures_data'][key] = df
            logger.info(f"Loaded {file}")
        
        # Load spot data
        for file in spot_files:
            key = file.split('_')[2]  # Extract key from filename
            file_path = os.path.join(args.input, file)
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            symbol_data['spot_data'][key] = df
            logger.info(f"Loaded {file}")
        
        # Load processed data
        for file in processed_files:
            key = '_'.join(file.split('_')[1:-1])  # Extract key from filename
            file_path = os.path.join(args.input, file)
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            symbol_data['processed_data'][key] = df
            logger.info(f"Loaded {file}")
        
        # Load signal data
        for file in signal_files:
            key = file.split('_')[1]  # Extract key from filename
            file_path = os.path.join(args.input, file)
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            symbol_data['signals'][key] = df
            logger.info(f"Loaded {file}")
        
        data[symbol] = symbol_data
    
    logger.info("Data loading completed")
    
    return data

def clean_data(data, args):
    """
    Clean loaded data.
    
    Args:
        data (Dict): Loaded data
        args: Command line arguments
        
    Returns:
        Dict: Cleaned data
    """
    logger.info("Cleaning data")
    
    cleaned_data = {}
    
    for symbol, symbol_data in data.items():
        logger.info(f"Cleaning data for {symbol}")
        
        cleaned_symbol_data = {
            'futures_data': {},
            'spot_data': {},
            'processed_data': {},
            'signals': {}
        }
        
        # Clean futures data
        for key, df in symbol_data['futures_data'].items():
            if df.empty:
                continue
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.ffill().bfill()
            
            # Filter by date range if timestamp column exists
            if 'timestamp' in df.columns:
                start_date = pd.to_datetime(args.start_date)
                end_date = pd.to_datetime(args.end_date)
                df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
            
            cleaned_symbol_data['futures_data'][key] = df
        
        # Clean spot data
        for key, df in symbol_data['spot_data'].items():
            if df.empty:
                continue
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.ffill().bfill()
            
            # Filter by date range if timestamp column exists
            if 'timestamp' in df.columns:
                start_date = pd.to_datetime(args.start_date)
                end_date = pd.to_datetime(args.end_date)
                df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
            
            cleaned_symbol_data['spot_data'][key] = df
        
        # Clean processed data
        for key, df in symbol_data['processed_data'].items():
            if df.empty:
                continue
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.ffill().bfill()
            
            # Filter by date range if timestamp column exists
            if 'timestamp' in df.columns:
                start_date = pd.to_datetime(args.start_date)
                end_date = pd.to_datetime(args.end_date)
                df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
            
            cleaned_symbol_data['processed_data'][key] = df
        
        # Clean signal data
        for key, df in symbol_data['signals'].items():
            if df.empty:
                continue
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.ffill().bfill()
            
            # Filter by date range if timestamp column exists
            if 'timestamp' in df.columns:
                start_date = pd.to_datetime(args.start_date)
                end_date = pd.to_datetime(args.end_date)
                df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
            
            cleaned_symbol_data['signals'][key] = df
        
        cleaned_data[symbol] = cleaned_symbol_data
    
    logger.info("Data cleaning completed")
    
    return cleaned_data

def run_backtest(data, args):
    """
    Run backtesting on the data.
    
    Args:
        data (Dict): Cleaned data
        args: Command line arguments
        
    Returns:
        Dict: Backtest results
    """
    logger.info("Running backtesting")
    
    # Create signal generator
    factor_combiner = FactorCombination(weights=WEIGHTS)
    signal_generator = SignalGenerator(factor_combiner=factor_combiner)
    
    backtest_results = {}
    
    for symbol, symbol_data in data.items():
        logger.info(f"Backtesting for {symbol}")
        
        # Get price data
        price_data = None
        
        if 'ohlc' in symbol_data['spot_data']:
            price_data = symbol_data['spot_data']['ohlc']
        
        if price_data is None or price_data.empty:
            logger.warning(f"No price data found for {symbol}")
            continue
        
        # Get normalized data
        normalized_data = None
        
        if 'normalized_data' in symbol_data['processed_data']:
            normalized_data = symbol_data['processed_data']['normalized_data']
        
        if normalized_data is None or normalized_data.empty:
            logger.warning(f"No normalized data found for {symbol}")
            continue
        
        # Merge price data with normalized data
        merged_data = pd.merge(
            normalized_data,
            price_data[['timestamp', 'close']],
            on='timestamp',
            how='inner'
        )
        
        if merged_data.empty:
            logger.warning(f"No merged data found for {symbol}")
            continue
        
        # Run backtest
        backtest_result = signal_generator.backtest_signals(merged_data, price_column='close')
        
        if backtest_result.empty:
            logger.warning(f"Backtest failed for {symbol}")
            continue
        
        # Calculate additional performance metrics
        total_return = backtest_result['cumulative_strategy_return'].iloc[-1]
        market_return = backtest_result['cumulative_market_return'].iloc[-1]
        
        # Calculate annualized returns
        days = (backtest_result['timestamp'].max() - backtest_result['timestamp'].min()).days
        years = days / 365
        
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        annualized_market_return = (1 + market_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Calculate Sharpe ratio
        daily_returns = backtest_result['strategy_return']
        risk_free_rate = 0.02  # Assuming 2% risk-free rate
        daily_risk_free = (1 + risk_free_rate) ** (1 / 365) - 1
        
        excess_returns = daily_returns - daily_risk_free
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # Calculate drawdown
        cumulative_returns = backtest_result['cumulative_strategy_return']
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Store results
        backtest_results[symbol] = {
            'backtest_data': backtest_result,
            'total_return': total_return,
            'market_return': market_return,
            'annualized_return': annualized_return,
            'annualized_market_return': annualized_market_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': backtest_result.attrs.get('win_rate', 0),
            'profit_factor': backtest_result.attrs.get('profit_factor', 0)
        }
        
        logger.info(f"Backtest results for {symbol}:")
        logger.info(f"  Total Return: {total_return:.2%}")
        logger.info(f"  Market Return: {market_return:.2%}")
        logger.info(f"  Annualized Return: {annualized_return:.2%}")
        logger.info(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.info(f"  Max Drawdown: {max_drawdown:.2%}")
        logger.info(f"  Win Rate: {backtest_result.attrs.get('win_rate', 0):.2%}")
        logger.info(f"  Profit Factor: {backtest_result.attrs.get('profit_factor', 0):.2f}")
    
    logger.info("Backtesting completed")
    
    return backtest_results

def analyze_correlations(data, args):
    """
    Analyze correlations between factors.
    
    Args:
        data (Dict): Cleaned data
        args: Command line arguments
        
    Returns:
        Dict: Correlation analysis results
    """
    logger.info("Analyzing correlations")
    
    correlation_results = {}
    
    for symbol, symbol_data in data.items():
        logger.info(f"Analyzing correlations for {symbol}")
        
        # Get normalized data
        normalized_data = None
        
        if 'normalized_data' in symbol_data['processed_data']:
            normalized_data = symbol_data['processed_data']['normalized_data']
        
        if normalized_data is None or normalized_data.empty:
            logger.warning(f"No normalized data found for {symbol}")
            continue
        
        # Select numeric columns for correlation analysis
        numeric_cols = normalized_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove timestamp and other non-factor columns
        exclude_cols = ['timestamp', 'signal', 'combined_signal']
        factor_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if not factor_cols:
            logger.warning(f"No factor columns found for {symbol}")
            continue
        
        # Calculate correlation matrix
        corr_matrix = normalized_data[factor_cols].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title(f'Factor Correlation Matrix - {symbol}')
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Save heatmap
        heatmap_file = os.path.join(args.output, f'{symbol}_correlation_heatmap.png')
        plt.savefig(heatmap_file)
        plt.close()
        
        logger.info(f"Saved correlation heatmap to {heatmap_file}")
        
        # Find highly correlated factors
        high_corr_pairs = []
        
        for i in range(len(factor_cols)):
            for j in range(i+1, len(factor_cols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.7:  # Threshold for high correlation
                    high_corr_pairs.append((factor_cols[i], factor_cols[j], corr))
        
        # Store results
        correlation_results[symbol] = {
            'correlation_matrix': corr_matrix,
            'high_correlation_pairs': high_corr_pairs,
            'heatmap_file': heatmap_file
        }
        
        logger.info(f"Found {len(high_corr_pairs)} highly correlated factor pairs for {symbol}")
    
    logger.info("Correlation analysis completed")
    
    return correlation_results

def analyze_factors(data, args):
    """
    Analyze factors using PCA and clustering.
    
    Args:
        data (Dict): Cleaned data
        args: Command line arguments
        
    Returns:
        Dict: Factor analysis results
    """
    logger.info("Analyzing factors")
    
    factor_analysis_results = {}
    
    for symbol, symbol_data in data.items():
        logger.info(f"Analyzing factors for {symbol}")
        
        # Get normalized data
        normalized_data = None
        
        if 'normalized_data' in symbol_data['processed_data']:
            normalized_data = symbol_data['processed_data']['normalized_data']
        
        if normalized_data is None or normalized_data.empty:
            logger.warning(f"No normalized data found for {symbol}")
            continue
        
        # Select numeric columns for factor analysis
        numeric_cols = normalized_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove timestamp and other non-factor columns
        exclude_cols = ['timestamp', 'signal', 'combined_signal']
        factor_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if not factor_cols:
            logger.warning(f"No factor columns found for {symbol}")
            continue
        
        # Prepare data for PCA
        X = normalized_data[factor_cols].dropna()
        
        if X.empty:
            logger.warning(f"No valid data for PCA for {symbol}")
            continue
        
        # Standardize data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Run PCA
        pca = PCA()
        pca_result = pca.fit_transform(X_scaled)
        
        # Calculate explained variance
        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        
        # Determine number of components for 90% variance
        n_components_90 = np.argmax(cumulative_variance >= 0.9) + 1
        
        # Plot explained variance
        plt.figure(figsize=(10, 6))
        plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.5, align='center',
                label='Individual explained variance')
        plt.step(range(1, len(cumulative_variance) + 1), cumulative_variance, where='mid',
                label='Cumulative explained variance')
        plt.axhline(y=0.9, color='r', linestyle='--', label='90% explained variance threshold')
        plt.axvline(x=n_components_90, color='g', linestyle='--', label=f'{n_components_90} components needed')
        plt.xlabel('Number of Principal Components')
        plt.ylabel('Explained Variance Ratio')
        plt.title(f'PCA Explained Variance - {symbol}')
        plt.legend(loc='best')
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Save PCA plot
        pca_file = os.path.join(args.output, f'{symbol}_pca_explained_variance.png')
        plt.savefig(pca_file)
        plt.close()
        
        logger.info(f"Saved PCA plot to {pca_file}")
        
        # Get component loadings
        loadings = pca.components_
        
        # Create loadings DataFrame
        loadings_df = pd.DataFrame(
            loadings.T,
            columns=[f'PC{i+1}' for i in range(loadings.shape[0])],
            index=factor_cols
        )
        
        # Save loadings to CSV
        loadings_file = os.path.join(args.output, f'{symbol}_pca_loadings.csv')
        loadings_df.to_csv(loadings_file)
        
        logger.info(f"Saved PCA loadings to {loadings_file}")
        
        # Run K-means clustering on the first 2 principal components
        if pca_result.shape[1] >= 2:
            X_pca = pca_result[:, :2]
            
            # Determine optimal number of clusters using silhouette score
            silhouette_scores = []
            max_clusters = min(10, X_pca.shape[0] // 5)  # Limit to 10 clusters or 1/5 of data points
            
            for n_clusters in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(X_pca)
                
                if len(np.unique(cluster_labels)) > 1:  # Ensure at least 2 clusters
                    silhouette_avg = silhouette_score(X_pca, cluster_labels)
                    silhouette_scores.append((n_clusters, silhouette_avg))
            
            if silhouette_scores:
                # Get optimal number of clusters
                optimal_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
                
                # Run K-means with optimal clusters
                kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(X_pca)
                
                # Plot clusters
                plt.figure(figsize=(10, 8))
                
                # Plot data points colored by cluster
                scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', alpha=0.7)
                
                # Plot cluster centers
                centers = kmeans.cluster_centers_
                plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.5, marker='X')
                
                plt.title(f'K-means Clustering (k={optimal_clusters}) on PCA Components - {symbol}')
                plt.xlabel('Principal Component 1')
                plt.ylabel('Principal Component 2')
                plt.colorbar(scatter, label='Cluster')
                
                # Save clustering plot
                cluster_file = os.path.join(args.output, f'{symbol}_kmeans_clustering.png')
                plt.savefig(cluster_file)
                plt.close()
                
                logger.info(f"Saved clustering plot to {cluster_file}")
                
                # Add cluster labels to original data
                cluster_df = X.copy()
                cluster_df['cluster'] = cluster_labels
                
                # Calculate factor means by cluster
                cluster_means = cluster_df.groupby('cluster').mean()
                
                # Save cluster means to CSV
                cluster_means_file = os.path.join(args.output, f'{symbol}_cluster_means.csv')
                cluster_means.to_csv(cluster_means_file)
                
                logger.info(f"Saved cluster means to {cluster_means_file}")
        
        # Store results
        factor_analysis_results[symbol] = {
            'pca_explained_variance': explained_variance,
            'cumulative_variance': cumulative_variance,
            'n_components_90': n_components_90,
            'loadings': loadings_df,
            'pca_file': pca_file,
            'loadings_file': loadings_file
        }
        
        if 'cluster_means' in locals():
            factor_analysis_results[symbol]['cluster_means'] = cluster_means
            factor_analysis_results[symbol]['cluster_file'] = cluster_file
            factor_analysis_results[symbol]['cluster_means_file'] = cluster_means_file
    
    logger.info("Factor analysis completed")
    
    return factor_analysis_results

def save_results(results, result_type, args):
    """
    Save results to files.
    
    Args:
        results (Dict): Results to save
        result_type (str): Type of results
        args: Command line arguments
    """
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if result_type == 'backtest':
        # Save backtest results
        for symbol, result in results.items():
            # Save backtest data
            if 'backtest_data' in result and not result['backtest_data'].empty:
                filename = os.path.join(args.output, f'{symbol}_backtest_data_{timestamp}.csv')
                result['backtest_data'].to_csv(filename, index=False)
                logger.info(f"Saved {filename}")
            
            # Save performance metrics
            metrics = {k: v for k, v in result.items() if k != 'backtest_data'}
            metrics_df = pd.DataFrame([metrics])
            
            filename = os.path.join(args.output, f'{symbol}_backtest_metrics_{timestamp}.csv')
            metrics_df.to_csv(filename, index=False)
            logger.info(f"Saved {filename}")
            
            # Create equity curve plot
            if 'backtest_data' in result and not result['backtest_data'].empty:
                plt.figure(figsize=(12, 6))
                
                plt.plot(result['backtest_data']['timestamp'], 
                         result['backtest_data']['cumulative_strategy_return'], 
                         label='Strategy')
                
                plt.plot(result['backtest_data']['timestamp'], 
                         result['backtest_data']['cumulative_market_return'], 
                         label='Market')
                
                plt.title(f'Equity Curve - {symbol}')
                plt.xlabel('Date')
                plt.ylabel('Cumulative Return')
                plt.legend()
                plt.grid(True)
                
                filename = os.path.join(args.output, f'{symbol}_equity_curve_{timestamp}.png')
                plt.savefig(filename)
                plt.close()
                
                logger.info(f"Saved {filename}")
    
    elif result_type == 'correlation':
        # Correlation results are saved during analysis
        pass
    
    elif result_type == 'factor_analysis':
        # Factor analysis results are saved during analysis
        pass

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info("Starting data processing script")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Load data
    data = load_data(args)
    
    if not data:
        logger.error("No data loaded")
        return
    
    # Clean data
    if args.mode in ['clean', 'backtest', 'correlation', 'factor_analysis', 'all']:
        cleaned_data = clean_data(data, args)
    else:
        cleaned_data = data
    
    # Run backtest
    if args.mode in ['backtest', 'all']:
        backtest_results = run_backtest(cleaned_data, args)
        save_results(backtest_results, 'backtest', args)
    
    # Analyze correlations
    if args.mode in ['correlation', 'all']:
        correlation_results = analyze_correlations(cleaned_data, args)
        save_results(correlation_results, 'correlation', args)
    
    # Analyze factors
    if args.mode in ['factor_analysis', 'all']:
        factor_analysis_results = analyze_factors(cleaned_data, args)
        save_results(factor_analysis_results, 'factor_analysis', args)
    
    logger.info("Data processing script completed")

if __name__ == "__main__":
    main()
