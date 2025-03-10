# Multi-Factor Quantitative Trading Strategy Documentation

This document provides detailed information about how the different factors are processed and combined in our quantitative trading strategy.

## Table of Contents
1. [Overview](#overview)
2. [Data Collection](#data-collection)
3. [Futures Market Factors](#futures-market-factors)
4. [Spot Market Factors](#spot-market-factors)
5. [Data Processing and Normalization](#data-processing-and-normalization)
6. [Factor Combination](#factor-combination)
7. [Signal Generation](#signal-generation)
8. [Backtesting and Performance Evaluation](#backtesting-and-performance-evaluation)

## Overview

The multi-factor quantitative trading strategy incorporates data from both futures and spot markets to generate trading signals. The strategy is designed to be modular, allowing for easy addition or removal of factors, and flexible, enabling customization of factor weights and signal thresholds.

The strategy follows these general steps:
1. Collect data from various sources
2. Process and normalize the data
3. Calculate individual factor signals
4. Combine factor signals to generate a final trading signal
5. Execute trades based on the signal (or backtest performance)

## Data Collection

The strategy collects data from multiple sources using a modular API client architecture. Each data source has a dedicated client class that handles authentication, rate limiting, and error handling.

### API Endpoints

The following API endpoints are used:

#### Coinglass API
- `/futures/openInterest`: Retrieves open interest data
- `/futures/fundingRate`: Retrieves funding rate data
- `/futures/liquidation`: Retrieves liquidation data

#### Exchange APIs (via CCXT)
- OHLCV data: Historical price and volume data
- Orderbook data: Current bid and ask orders

### Modular Components for Data Collection

The data collection system is built with the following modular components:

1. **Base API Client**: Provides common functionality for all API clients
   - HTTP request handling
   - Authentication
   - Error handling
   - Rate limiting

2. **Coinglass Client**: Specialized client for Coinglass API
   - Open interest data collection
   - Funding rate data collection
   - Liquidation data collection

3. **Exchange Client**: Specialized client for cryptocurrency exchanges
   - OHLCV data collection
   - Orderbook data collection
   - Factory pattern for creating exchange-specific clients

4. **Data Collectors**: High-level components that orchestrate data collection
   - `FuturesDataCollector`: Collects futures market data
   - `SpotDataCollector`: Collects spot market data

## Futures Market Factors

### Open Interest from Historical OHLC Data

Open Interest represents the total number of outstanding derivative contracts that have not been settled. It provides insights into market sentiment and potential trend strength.

#### Processing
1. **Data Collection**: Open interest data is collected from Coinglass API for multiple exchanges
2. **Aggregation**: Data is aggregated by exchange and timestamp
3. **Change Calculation**: Percentage change in open interest is calculated
4. **Rolling Statistics**: Moving averages and standard deviations are calculated for different time windows
5. **Z-Score Calculation**: Open interest values are normalized using z-scores to identify unusual changes

#### Significance
- **Increasing Open Interest + Rising Price**: Strong bullish trend
- **Increasing Open Interest + Falling Price**: Strong bearish trend
- **Decreasing Open Interest + Rising/Falling Price**: Trend weakening

### Funding Rates Weighted by Open Interest

Funding rates are periodic payments exchanged between long and short positions in perpetual futures contracts. They indicate market sentiment and potential price reversals.

#### Processing
1. **Data Collection**: Funding rate data is collected from Coinglass API for multiple exchanges
2. **Weighting**: Funding rates are weighted by the open interest of each exchange
3. **Aggregation**: Weighted funding rates are aggregated to create a single indicator

#### Significance
- **Positive Funding Rate**: Longs pay shorts, indicating bullish sentiment
- **Negative Funding Rate**: Shorts pay longs, indicating bearish sentiment
- **Extreme Funding Rates**: Potential for price reversal due to overcrowded positions

### Aggregated Orderbook Data

Orderbook data provides insights into market microstructure and short-term supply and demand dynamics.

#### Processing
1. **Data Collection**: Orderbook data is collected from Binance, OKX, and Bybit
2. **Metrics Calculation**:
   - Bid-ask spread
   - Order book imbalance (ratio of bid to ask volume)
   - Market depth at different price levels
3. **Aggregation**: Metrics are aggregated across exchanges

#### Significance
- **Positive Imbalance**: More buy orders than sell orders, indicating bullish pressure
- **Negative Imbalance**: More sell orders than buy orders, indicating bearish pressure
- **Spread Widening**: Increasing volatility or decreasing liquidity

### RSI Technical Indicator

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.

#### Processing
1. **Data Collection**: OHLCV data is collected from exchanges
2. **RSI Calculation**: RSI is calculated using the standard formula with a 14-period window
3. **Signal Generation**: Overbought and oversold levels are identified

#### Significance
- **RSI > 70**: Overbought condition, potential for price reversal (bearish)
- **RSI < 30**: Oversold condition, potential for price reversal (bullish)
- **RSI Divergence**: Divergence between RSI and price can indicate potential reversals

### Liquidation Heat Map

Liquidation data provides insights into forced position closures, which can lead to cascading price movements.

#### Processing
1. **Data Collection**: Liquidation data is collected from Coinglass API
2. **Aggregation**: Data is aggregated by timestamp
3. **Ratio Calculation**: Ratio of long to short liquidations is calculated
4. **Intensity Calculation**: Liquidation intensity is calculated relative to historical averages

#### Significance
- **High Long Liquidations**: Potential for downward price cascade
- **High Short Liquidations**: Potential for upward price cascade
- **Liquidation Clusters**: Areas of significant price support or resistance

## Spot Market Factors

### OHLC Market Data

OHLC (Open, High, Low, Close) data provides the basic price information for technical analysis.

#### Processing
1. **Data Collection**: OHLC data is collected from exchanges
2. **Normalization**: Price data is normalized to enable comparison across different assets
3. **Return Calculation**: Percentage returns are calculated for different time periods

#### Significance
- **Price Trends**: Direction and strength of market movements
- **Volatility**: Magnitude of price fluctuations
- **Support/Resistance Levels**: Areas of historical price significance

### Orderbook Data

Similar to futures orderbook data, spot orderbook data provides insights into market microstructure.

#### Processing
1. **Data Collection**: Orderbook data is collected from exchanges
2. **Metrics Calculation**:
   - Bid-ask spread
   - Order book imbalance
   - Market depth
3. **Comparison**: Spot orderbook metrics are compared with futures orderbook metrics

#### Significance
- **Spot-Futures Divergence**: Differences in orderbook structure between spot and futures markets can indicate potential arbitrage opportunities or market inefficiencies

### Coinbase Premium Index

The Coinbase Premium Index measures the price difference between Coinbase (USD) and Binance (USDT) for the same asset.

#### Processing
1. **Data Collection**: Price data is collected from Coinbase and Binance
2. **Premium Calculation**: Price difference is calculated and normalized as a percentage
3. **Moving Average**: Moving averages of the premium are calculated for different time windows
4. **Z-Score Calculation**: Premium values are normalized using z-scores

#### Significance
- **Positive Premium**: Higher prices on Coinbase, indicating stronger buying pressure from US investors
- **Negative Premium**: Lower prices on Coinbase, indicating stronger selling pressure from US investors
- **Premium Changes**: Rapid changes in premium can precede market-wide price movements

### Bitfinex Margin Long/Short Ratio

The Bitfinex margin long/short ratio measures the relative size of long and short positions on Bitfinex.

#### Processing
1. **Data Collection**: Margin data is collected from Bitfinex
2. **Ratio Calculation**: Ratio of long to short positions is calculated
3. **Log Transformation**: Ratio is log-transformed to center around zero
4. **Moving Average**: Moving averages of the ratio are calculated for different time windows
5. **Z-Score Calculation**: Ratio values are normalized using z-scores

#### Significance
- **High Ratio**: More long positions than short positions, indicating bullish sentiment
- **Low Ratio**: More short positions than long positions, indicating bearish sentiment
- **Extreme Ratios**: Potential for contrarian signals due to overcrowded positioning

## Data Processing and Normalization

### Data Processing

The data processing system transforms raw data into usable factors for the strategy. Key processing steps include:

1. **Cleaning**:
   - Handling missing values
   - Removing duplicates
   - Filtering outliers

2. **Feature Engineering**:
   - Calculating percentage changes
   - Computing moving averages
   - Deriving momentum indicators
   - Calculating ratios and spreads

3. **Time Alignment**:
   - Ensuring all data is properly aligned by timestamp
   - Resampling to consistent time intervals
   - Handling different time zones

### Normalization

Normalization ensures that factors with different scales can be compared and combined effectively. The strategy uses two main normalization methods:

1. **Z-Score Normalization**:
   - Subtracts the mean and divides by the standard deviation
   - Centers data around zero with a standard deviation of one
   - Useful for identifying unusual values relative to historical distribution

2. **Min-Max Scaling**:
   - Scales data to a specific range (typically -1 to 1)
   - Preserves the shape of the distribution
   - Useful for factors with bounded ranges

The normalization process is adaptive, with parameters (mean, standard deviation, min, max) calculated on a rolling basis to account for changing market conditions.

## Factor Combination

The strategy combines multiple factors to generate a single trading signal. The combination process is designed to be flexible and adaptable to different market conditions.

### Weighting Methods

The strategy supports several weighting methods:

1. **Equal Weighting**:
   - All factors receive the same weight
   - Simple and robust approach

2. **Fixed Weighting**:
   - Factors receive predetermined weights based on prior research
   - Current default weights:
     - Open Interest: 20%
     - Funding Rate: 20%
     - Orderbook Imbalance: 15%
     - RSI: 15%
     - Coinbase Premium: 15%
     - Bitfinex Margin Ratio: 15%

3. **Dynamic Weighting**:
   - Weights are adjusted based on recent factor performance
   - Factors with higher predictive power receive higher weights
   - Implemented using correlation analysis and optimization techniques

### Optimization Techniques

The strategy includes several methods for optimizing factor weights:

1. **Correlation Analysis**:
   - Identifies relationships between factors
   - Helps avoid overweighting correlated factors
   - Used to create orthogonal factor sets

2. **Principal Component Analysis (PCA)**:
   - Reduces dimensionality of the factor space
   - Identifies the most important underlying factors
   - Helps eliminate redundant information

3. **Machine Learning Optimization**:
   - Uses historical data to optimize weights
   - Supports various algorithms (linear regression, genetic algorithms, etc.)
   - Includes cross-validation to prevent overfitting

### Efficient Factor Combination

The most efficient way to combine factors involves several key principles:

1. **Decorrelation**:
   - Identify and remove highly correlated factors
   - Use PCA to create orthogonal factors
   - Weight factors inversely to their correlation with other factors

2. **Regime Detection**:
   - Identify different market regimes (trending, ranging, volatile)
   - Adjust factor weights based on the current regime
   - Use different factor sets for different regimes

3. **Adaptive Timeframes**:
   - Use different time windows for different factors
   - Combine short-term and long-term signals
   - Weight factors based on their predictive horizon

4. **Signal Confirmation**:
   - Require confirmation from multiple factor categories
   - Increase conviction when futures and spot factors align
   - Reduce position size when factors disagree

## Signal Generation

The strategy generates trading signals based on the combined factor score. The signal generation process includes:

1. **Thresholding**:
   - Combined score > 0.2: Buy signal
   - Combined score < -0.2: Sell signal
   - Otherwise: Neutral

2. **Signal Filtering**:
   - Minimum holding period to reduce trading frequency
   - Confirmation requirements to reduce false signals
   - Trend alignment to avoid trading against strong trends

3. **Position Sizing**:
   - Signal strength determines position size
   - Risk-based position sizing based on recent volatility
   - Maximum position limits to control risk

## Backtesting and Performance Evaluation

The strategy includes comprehensive backtesting capabilities to evaluate performance:

1. **Performance Metrics**:
   - Total return
   - Annualized return
   - Sharpe ratio
   - Maximum drawdown
   - Win rate
   - Profit factor

2. **Visualization**:
   - Equity curves
   - Drawdown charts
   - Factor contribution analysis
   - Signal distribution

3. **Sensitivity Analysis**:
   - Factor weight sensitivity
   - Signal threshold sensitivity
   - Time window sensitivity
   - Transaction cost sensitivity

4. **Walk-Forward Testing**:
   - Out-of-sample testing
   - Parameter stability analysis
   - Regime change analysis
