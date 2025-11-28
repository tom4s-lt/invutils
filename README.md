# invutils

A lightweight Python package for retrieving cryptocurrency price data from CoinGecko and DefiLlama APIs.

## Features

- 🪙 Current and historical cryptocurrency prices from CoinGecko
- 📊 Historical price data from DefiLlama
- 🚀 Simple, intuitive API
- 🔒 Type hints and proper error handling
- 📦 Minimal dependencies

## Installation

```bash
pip install git+https://github.com/xtom4s/invutils
```

## Quick Start

```python
from invutils import gecko_price_current, gecko_price_hist, llama_price_hist

# Get current prices from CoinGecko (requires API key)
prices = gecko_price_current('bitcoin,ethereum,solana', api_key='your-api-key-here')
print(prices)
# {'bitcoin': {'usd': 45230.12}, 'ethereum': {'usd': 2341.56}, ...}

# Get historical prices from CoinGecko (requires API key)
history = gecko_price_hist('ethereum', days=30, api_key='your-api-key-here')
print(history)
# {'prices': [[timestamp1, price1], [timestamp2, price2], ...]}

# Get prices from DefiLlama (no API key needed)
llama_prices = llama_price_hist('ethereum:0x0000000000000000000000000000000000000000')
print(llama_prices)
# {'ethereum:0x0000...': {'symbol': 'ETH', 'price': 2341.56, ...}}
```

## API Information

- CoinGecko
    - **Documentation**: [CoinGecko API Docs (Demo)](https://docs.coingecko.com/v3.0.1/reference/authentication) (package uses Demo endpoints)
    - **API Key**: Required - [Get free Demo API key here](https://www.coingecko.com/en/api/pricing)
    - **Token identifiers**: Use CoinGecko IDs (e.g., `bitcoin`, `ethereum`, `usd-coin`)
- DefiLlama
    - **Documentation**: [DefiLlama API Docs](https://defillama.com/docs/api)
    - **API Key**: No key required, it's fully open and free
    - **Token identifiers**: Use format `chain:address` (e.g., `ethereum:0x6b175474e89094c44da98b954eedeac495271d0f` for DAI)

## API Reference

### `gecko_price_current(id_gecko, vs_currencies='usd', api_key=None)`

Get current cryptocurrency prices from CoinGecko.

**Parameters:**
- `id_gecko` (str): Single coin ID or comma-separated IDs (e.g., `'bitcoin'` or `'bitcoin,ethereum'`)
- `vs_currencies` (str, optional): Currency to price against (default: `'usd'`)
- `api_key` (str, required): CoinGecko Demo API key - required for API access (default: `None`)

**Returns:**
- `dict`: Price data for requested coins, or `None` on error

**Example:**
```python
# With Demo API key (required)
gecko_price_current('bitcoin,ethereum', api_key='your-api-key-here')

# Multiple currencies
gecko_price_current('bitcoin', vs_currencies='usd,eur,gbp', api_key='your-api-key-here')
```

### `gecko_price_hist(id_gecko, vs_currency='usd', days='max', api_key=None)`

Get historical price data from CoinGecko.

**Parameters:**
- `id_gecko` (str): CoinGecko coin ID (e.g., `'ethereum'`)
- `vs_currency` (str, optional): Currency to price against (default: `'usd'`)
- `days` (int or str, optional): Days of history (`1-90` for hourly, `>90` for daily, or `'max'`)
- `api_key` (str, required): CoinGecko Demo API key - required for API access (default: `None`)

**Returns:**
- `dict`: Dictionary with `'prices'` key containing `[[timestamp_ms, price], ...]`, or `None` on error

**Example:**
```python
# Get 30 days of historical prices
gecko_price_hist('ethereum', days=30, api_key='your-api-key-here')

# Get all available historical data
gecko_price_hist('bitcoin', days='max', api_key='your-api-key-here')
```

### `llama_price_hist(id_llama, timestamp=None)`

Get historical/current prices from DefiLlama.

**Parameters:**
- `id_llama` (str): DefiLlama ID in format `chain:address` or comma-separated IDs
- `timestamp` (int, optional): UNIX timestamp for historical prices (default: current time)

**Returns:**
- `dict`: Price data with coin addresses as keys, or `None` on error

**Example:**
```python
# Current prices
llama_price_hist('ethereum:0x6b175474e89094c44da98b954eedeac495271d0f')

# Historical prices
llama_price_hist('ethereum:0x6b175474e89094c44da98b954eedeac495271d0f', timestamp=1640000000)

# Multiple tokens
llama_price_hist('ethereum:0x6b175474e89094c44da98b954eedeac495271d0f,bsc:0xe9e7cea3dedca5984780bafc599bd69add087d56')
```

## Token ID Formats

### CoinGecko IDs
Find coin IDs on the CoinGecko website or API:
- Bitcoin: `bitcoin`
- Ethereum: `ethereum`
- USD Coin: `usd-coin`
- DAI: `dai`

### DefiLlama IDs
Format: `chain:contract_address`
- Native assets use zero address: `ethereum:0x0000000000000000000000000000000000000000`
- ERC-20 tokens: `ethereum:0x6b175474e89094c44da98b954eedeac495271d0f` (DAI)
- BSC tokens: `bsc:0xe9e7cea3dedca5984780bafc599bd69add087d56` (BUSD)

## Error Handling

All functions return `None` on error and log the issue. Common errors:
- Invalid coin IDs
- Network issues
- API rate limits
- Malformed responses

## Requirements

- Python ≥ 3.7
- requests ≥ 2.25.0
- pandas ≥ 1.2.0

## Changelog

All notable changes to this project will be documented here.

### [1.1.0] - 2025-11-27

**Added:**
- CoinGecko price functions (current and historical)
- DefiLlama historical price function
- API key support for CoinGecko Demo tier
- Comprehensive error handling and logging
- Type hints throughout the codebase
- Clean public API via `__init__.py`
- Simple configuration management

**Features:**
- `gecko_price_current()` - Get current cryptocurrency prices from CoinGecko
- `gecko_price_hist()` - Get historical price data from CoinGecko
- `llama_price_hist()` - Get historical/current prices from DefiLlama
- Support for multiple coins in a single request
- Configurable timeout settings
- Detailed error logging for debugging

### [1.0.0] - Initial Release

**Added:**
- Initial package structure
- Basic API integration framework

## License

MIT

## References

- [defi](https://github.com/gauss314/defi) - DeFi tools by gauss314
- [ctc](https://github.com/fei-protocol/checkthechain) - Ethereum data analysis
- [defi-protocols](https://github.com/KarpatkeyDAO/defi-protocols) - Python library by Karpatkey
