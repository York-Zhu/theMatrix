"""
Main module for the crypto quantitative trading strategy.
Orchestrates data collection, processing, and signal generation.
"""
import pandas as pd
import numpy as np
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import os

from src.data_collection.futures_data import FuturesDataCollector
from src.data_collection.spot_data import SpotDataCollector
from src.data_processing.processor import DataProcessor
from src.data_processing.normalizer import DataNormalizer
from src.strategy.factor_combination import FactorCombination
from src.strategy.signal_generator import SignalGenerator
from src.utils.logger import main_logger as logger
from src.utils.config import (
    DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, DEFAULT_LIMIT, DEFAULT_EXCHANGES,
    WEIGHTS
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Crypto Quantitative Trading Strategy')
    
    parser.add_argument('--symbols', nargs='+', default=DEFAULT_SYMBOLS,
                        help='Symbols to collect data for')
    parser.add_argument('--timeframe', default=DEFAULT_TIMEFRAME,
                        help='Timeframe for data collection')
    parser.add_argument('--limit', type=int, default=DEFAULT_LIMIT,
                        help='Number of data points to fetch')
    parser.add_argument('--exchanges', nargs='+', default=DEFAULT_EXCHANGES,
                        help='Exchanges to collect data from')
    parser.add_argument('--mode', choices=['collect', 'process', 'backtest', 'all'],
                        default='all', help='Mode of operation')
    parser.add_argument('--output', default='data',
                        help='Output directory for data files')
    
    return parser.parse_args()

def collect_data(args):
    """
    Collect data from various sources.
    
    Args:
        args: Command line arguments
        
    Returns:
        Dict: Collected data
    """
    logger.info("Starting data collection")
    
    # Create data collectors
    futures_collector = FuturesDataCollector(
        symbols=args.symbols,
        timeframe=args.timeframe,
        limit=args.limit,
        exchanges=args.exchanges
    )
    
    spot_collector = SpotDataCollector(
        symbols=args.symbols,
        timeframe=args.timeframe,
        limit=args.limit
    )
    
    # Collect data
    futures_data = {}
    spot_data = {}
    
    for symbol in args.symbols:
        logger.info(f"Collecting data for {symbol}")
        
        # Collect futures data
        symbol_futures_data = futures_collector.collect_all_futures_data(symbol)
        futures_data[symbol] = symbol_futures_data
        
        # Collect spot data
        symbol_spot_data = spot_collector.collect_all_spot_data(symbol)
        spot_data[symbol] = symbol_spot_data
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    logger.info("Data collection completed")
    
    return {
        'futures_data': futures_data,
        'spot_data': spot_data
    }

def process_data(collected_data, args):
    """
    Process collected data.
    
    Args:
        collected_data (Dict): Collected data
        args: Command line arguments
        
    Returns:
        Dict: Processed data
    """
    logger.info("Starting data processing")
    
    # Create data processor and normalizer
    processor = DataProcessor()
    normalizer = DataNormalizer(normalization_method='z-score')
    
    # Process data
    processed_data = {}
    
    for symbol in args.symbols:
        logger.info(f"Processing data for {symbol}")
        
        # Get data for the symbol
        symbol_futures_data = collected_data['futures_data'].get(symbol, {})
        symbol_spot_data = collected_data['spot_data'].get(symbol, {})
        
        # Process futures data
        processed_futures_data = processor.process_futures_data(symbol_futures_data)
        
        # Process spot data
        processed_spot_data = processor.process_spot_data(symbol_spot_data)
        
        # Combine processed data
        combined_data = processor.combine_processed_data(
            processed_futures_data, processed_spot_data
        )
        
        # Normalize data
        normalized_data = normalizer.normalize_dataframe(combined_data)
        
        # Store processed data
        processed_data[symbol] = {
            'futures_data': processed_futures_data,
            'spot_data': processed_spot_data,
            'combined_data': combined_data,
            'normalized_data': normalized_data
        }
    
    logger.info("Data processing completed")
    
    return processed_data

def generate_signals(processed_data, args):
    """
    Generate trading signals from processed data.
    
    Args:
        processed_data (Dict): Processed data
        args: Command line arguments
        
    Returns:
        Dict: Trading signals
    """
    logger.info("Starting signal generation")
    
    # Create factor combiner and signal generator
    factor_combiner = FactorCombination(weights=WEIGHTS)
    signal_generator = SignalGenerator(factor_combiner=factor_combiner)
    
    # Generate signals
    signals = {}
    
    for symbol in args.symbols:
        logger.info(f"Generating signals for {symbol}")
        
        # Get normalized data for the symbol
        normalized_data = processed_data[symbol]['normalized_data']
        
        # Generate individual signals
        individual_signals = signal_generator.generate_individual_signals(normalized_data)
        
        # Generate combined signal
        combined_signal = signal_generator.generate_combined_signal(individual_signals)
        
        # Store signals
        signals[symbol] = {
            'individual_signals': individual_signals,
            'combined_signal': combined_signal
        }
        
        # Log signal
        signal_value = combined_signal['signal'].iloc[0]
        signal_text = "BUY" if signal_value == 1 else "SELL" if signal_value == -1 else "NEUTRAL"
        logger.info(f"Signal for {symbol}: {signal_text} ({signal_value})")
    
    logger.info("Signal generation completed")
    
    return signals

def save_data(data, data_type, args):
    """
    Save data to files.
    
    Args:
        data (Dict): Data to save
        data_type (str): Type of data
        args: Command line arguments
    """
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save data for each symbol
    for symbol, symbol_data in data.items():
        if data_type == 'collected':
            # Save futures data
            for key, df in symbol_data['futures_data'].items():
                if not df.empty:
                    filename = f"{args.output}/{symbol}_futures_{key}_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    logger.info(f"Saved {filename}")
            
            # Save spot data
            for key, df in symbol_data['spot_data'].items():
                if not df.empty:
                    filename = f"{args.output}/{symbol}_spot_{key}_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    logger.info(f"Saved {filename}")
                    
        elif data_type == 'processed':
            # Save processed data
            for key, value in symbol_data.items():
                if isinstance(value, pd.DataFrame) and not value.empty:
                    filename = f"{args.output}/{symbol}_{key}_{timestamp}.csv"
                    value.to_csv(filename, index=False)
                    logger.info(f"Saved {filename}")
                elif isinstance(value, dict):
                    for subkey, df in value.items():
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            filename = f"{args.output}/{symbol}_{key}_{subkey}_{timestamp}.csv"
                            df.to_csv(filename, index=False)
                            logger.info(f"Saved {filename}")
                            
        elif data_type == 'signals':
            # Save signals
            for key, df in symbol_data.items():
                if not df.empty:
                    filename = f"{args.output}/{symbol}_{key}_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    logger.info(f"Saved {filename}")

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info("Starting crypto quantitative trading strategy")
    
    # Collect data
    if args.mode in ['collect', 'all']:
        collected_data = collect_data(args)
        save_data(collected_data, 'collected', args)
    else:
        collected_data = None
    
    # Process data
    if args.mode in ['process', 'backtest', 'all']:
        if collected_data is None:
            logger.error("No data collected for processing")
            return
        
        processed_data = process_data(collected_data, args)
        save_data(processed_data, 'processed', args)
    else:
        processed_data = None
    
    # Generate signals
    if args.mode in ['backtest', 'all']:
        if processed_data is None:
            logger.error("No processed data for signal generation")
            return
        
        signals = generate_signals(processed_data, args)
        save_data(signals, 'signals', args)
    
    logger.info("Crypto quantitative trading strategy completed")

if __name__ == "__main__":
    main()
