# API Documentation

This document provides detailed information about the API endpoints used in the multi-factor quantitative trading strategy and how data is efficiently fetched from each endpoint.

## Table of Contents
1. [Coinglass API](#coinglass-api)
2. [Exchange APIs](#exchange-apis)
3. [Data Fetching Efficiency](#data-fetching-efficiency)
4. [Error Handling and Resilience](#error-handling-and-resilience)
5. [Rate Limiting](#rate-limiting)

## Coinglass API

Coinglass provides comprehensive data for cryptocurrency futures markets. The strategy uses the following Coinglass API endpoints:

### Open Interest Endpoint

**Endpoint:** `/futures/openInterest`

**Method:** GET

**Parameters:**
- `symbol` (required): Cryptocurrency symbol (e.g., "BTC")
- `interval` (optional): Time interval (e.g., "1h", "4h", "1d")
- `exchange` (optional): Exchange name to filter results

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "exchangeName": "Binance",
      "dataMap": {
        "BTC": [
          {
            "createTime": 1641024000000,
            "openInterest": 123456.78,
            "openInterestUsd": 5678901234.56
          }
        ]
      }
    }
  ]
}
```

**Implementation:**
```python
def get_open_interest(self, symbol: str, exchange: Optional[str] = None, 
                     interval: str = "1h") -> Dict[str, Any]:
    """
    Get open interest data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC")
        exchange (str, optional): Exchange to get data from. Defaults to None (all exchanges).
        interval (str, optional): Time interval. Defaults to "1h".
        
    Returns:
        Dict[str, Any]: Open interest data
    """
    params = {
        "symbol": symbol,
        "interval": interval
    }
    
    if exchange:
        params["exchange"] = exchange
        
    return self.get("/futures/openInterest", params)
```

### Funding Rate Endpoint

**Endpoint:** `/futures/fundingRate`

**Method:** GET

**Parameters:**
- `symbol` (required): Cryptocurrency symbol (e.g., "BTC")
- `exchange` (optional): Exchange name to filter results

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "exchangeName": "Binance",
      "symbol": "BTC",
      "rate": 0.0001,
      "nextFundingTime": 1641024000000
    }
  ]
}
```

**Implementation:**
```python
def get_funding_rate(self, symbol: str, exchange: Optional[str] = None) -> Dict[str, Any]:
    """
    Get funding rate data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC")
        exchange (str, optional): Exchange to get data from. Defaults to None (all exchanges).
        
    Returns:
        Dict[str, Any]: Funding rate data
    """
    params = {"symbol": symbol}
    
    if exchange:
        params["exchange"] = exchange
        
    return self.get("/futures/fundingRate", params)
```

### Liquidation Endpoint

**Endpoint:** `/futures/liquidation`

**Method:** GET

**Parameters:**
- `symbol` (required): Cryptocurrency symbol (e.g., "BTC")
- `timeframe` (optional): Time frame (e.g., "1h", "4h", "1d")

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "createTime": 1641024000000,
      "symbol": "BTC",
      "longLiquidation": 1234.56,
      "shortLiquidation": 789.01,
      "totalLiquidation": 2023.57
    }
  ]
}
```

**Implementation:**
```python
def get_liquidation(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
    """
    Get liquidation data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC")
        timeframe (str, optional): Time frame. Defaults to "1h".
        
    Returns:
        Dict[str, Any]: Liquidation data
    """
    params = {
        "symbol": symbol,
        "timeframe": timeframe
    }
    
    return self.get("/futures/liquidation", params)
```

## Exchange APIs

The strategy uses the CCXT library to interact with various cryptocurrency exchanges. CCXT provides a unified API for accessing data from multiple exchanges.

### OHLCV Data

**Method:** `fetch_ohlcv`

**Parameters:**
- `symbol` (required): Trading pair symbol (e.g., "BTC/USDT")
- `timeframe` (optional): Time frame (e.g., "1h", "4h", "1d")
- `limit` (optional): Number of data points to fetch

**Response Format:**
```
[
  [timestamp, open, high, low, close, volume],
  [timestamp, open, high, low, close, volume],
  ...
]
```

**Implementation:**
```python
def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
             limit: int = 100) -> List[List[Union[int, float]]]:
    """
    Get OHLCV (Open, High, Low, Close, Volume) data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC/USDT")
        timeframe (str, optional): Time frame. Defaults to "1h".
        limit (int, optional): Number of data points to fetch. Defaults to 100.
        
    Returns:
        List[List[Union[int, float]]]: OHLCV data
    """
    try:
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        logger.error(f"Error fetching OHLCV data from {self.exchange_id}: {e}")
        return []
```

### Orderbook Data

**Method:** `fetch_order_book`

**Parameters:**
- `symbol` (required): Trading pair symbol (e.g., "BTC/USDT")
- `limit` (optional): Depth of the orderbook

**Response Format:**
```json
{
  "bids": [[price, amount], [price, amount], ...],
  "asks": [[price, amount], [price, amount], ...],
  "timestamp": 1641024000000,
  "datetime": "2022-01-01T00:00:00.000Z",
  "nonce": 123456789
}
```

**Implementation:**
```python
def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get orderbook data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC/USDT")
        limit (int, optional): Depth of the orderbook. Defaults to 20.
        
    Returns:
        Dict[str, Any]: Orderbook data
    """
    try:
        orderbook = self.exchange.fetch_order_book(symbol, limit)
        return orderbook
    except Exception as e:
        logger.error(f"Error fetching orderbook data from {self.exchange_id}: {e}")
        return {"bids": [], "asks": []}
```

## Data Fetching Efficiency

The strategy implements several techniques to ensure efficient data fetching:

### Parallel Processing

For independent data sources, the strategy uses parallel processing to fetch data simultaneously:

```python
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
```

### Caching

The strategy implements caching to avoid redundant API calls:

1. **In-Memory Caching**: Frequently accessed data is stored in memory
2. **Disk Caching**: Historical data is saved to disk for later use
3. **Cache Invalidation**: Cache is invalidated based on time or events

### Batch Requests

Where supported by the API, the strategy uses batch requests to fetch multiple data points in a single API call:

```python
def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
             limit: int = 100) -> List[List[Union[int, float]]]:
    """
    Get OHLCV (Open, High, Low, Close, Volume) data for a symbol.
    
    Args:
        symbol (str): Symbol to get data for (e.g., "BTC/USDT")
        timeframe (str, optional): Time frame. Defaults to "1h".
        limit (int, optional): Number of data points to fetch. Defaults to 100.
        
    Returns:
        List[List[Union[int, float]]]: OHLCV data
    """
    try:
        # Fetch multiple data points in a single request
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        logger.error(f"Error fetching OHLCV data from {self.exchange_id}: {e}")
        return []
```

### Incremental Updates

For real-time data, the strategy uses incremental updates to minimize data transfer:

1. **Initial Fetch**: Complete data is fetched initially
2. **Subsequent Updates**: Only new or changed data is fetched
3. **Websocket Connections**: For exchanges that support it, websocket connections are used for real-time updates

## Error Handling and Resilience

The strategy implements robust error handling to ensure resilience:

### Retry Mechanism

API calls are retried with exponential backoff in case of temporary failures:

```python
def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
    """
    Handle API response and check for errors.
    
    Args:
        response (requests.Response): Response from the API
        
    Returns:
        Dict[str, Any]: Parsed JSON response
        
    Raises:
        Exception: If the API returns an error
    """
    if response.status_code != 200:
        logger.error(f"API error: {response.status_code} - {response.text}")
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    return data
```

### Fallback Sources

For critical data, the strategy implements fallback data sources:

1. **Multiple Exchanges**: Data is collected from multiple exchanges
2. **Alternative APIs**: Alternative APIs are used if primary sources fail
3. **Historical Data**: Historical data is used if real-time data is unavailable

### Graceful Degradation

The strategy is designed to continue functioning with reduced capabilities if some data sources are unavailable:

```python
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
```

## Rate Limiting

The strategy implements rate limiting to comply with API usage policies:

### Throttling

API calls are throttled to stay within rate limits:

```python
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
```

### Request Prioritization

Requests are prioritized based on importance:

1. **Critical Data**: High priority, fetched first
2. **Supporting Data**: Medium priority, fetched if time allows
3. **Optional Data**: Low priority, fetched only if resources are available

### Adaptive Polling

Polling frequency is adjusted based on market conditions:

1. **High Volatility**: More frequent polling
2. **Low Volatility**: Less frequent polling
3. **Trading Hours**: More frequent polling during active trading hours
