# Crypto Quantitative Trading Strategy

A multi-factor quantitative trading strategy implementation using market data from Coinglass API, incorporating both futures and spot market indicators.

## Features

- Data collection from multiple sources (Coinglass, Binance, OKX, Bybit, Coinbase, Bitfinex)
- Processing of futures market factors (Open Interest, Funding Rates, Orderbook data, RSI)
- Processing of spot market factors (OHLC data, Orderbook data, Coinbase Premium Index, Bitfinex margin ratios)
- Modular components for data fetching, processing, and strategy calculation
- Data processing scripts for cleaning, backtesting, and correlation analysis

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

## Project Structure

```
crypto-quant-trading/
├── README.md
├── requirements.txt
├── setup.py
└── src/
    ├── __init__.py
    ├── main.py
    ├── data_collection/
    │   ├── __init__.py
    │   ├── futures_data.py
    │   └── spot_data.py
    ├── data_processing/
    │   ├── __init__.py
    │   ├── processor.py
    │   └── normalizer.py
    ├── strategy/
    │   ├── __init__.py
    │   ├── factor_combination.py
    │   └── signal_generator.py
    ├── utils/
    │   ├── __init__.py
    │   ├── api_client.py
    │   ├── config.py
    │   └── logger.py
    └── tests/
        └── __init__.py
```

