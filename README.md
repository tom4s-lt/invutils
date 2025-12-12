# invutils

A lightweight Python package for retrieving cryptocurrency price data from CoinGecko and DefiLlama APIs.

## Features

- 🪙 Current and historical cryptocurrency prices from CoinGecko
- 📊 Historical price data from DefiLlama
- 🚀 Simple, intuitive API with standardized output format
- 🔒 Type hints and proper error handling
- 📦 Minimal dependencies

## Installation

```bash
pip install git+https://github.com/xtom4s/invutils
```

## Quick Start

```python
# Import from main package
from invutils import gecko_price_current, gecko_price_historical, llama_price_historical

# Or import from organized submodules (v1.2.0+)
from invutils.prices import gecko_price_current
from invutils.prices.coingecko import gecko_price_current

# Get current prices from CoinGecko (requires API key)
result = gecko_price_current('bitcoin,ethereum', api_key='your-api-key-here')
print(result)
# {'source': 'coingecko', 'status': 'success', 'count': 2, 'data': [...]}

# Get historical prices from CoinGecko (requires API key)
result = gecko_price_historical('ethereum', days=7, api_key='your-api-key-here')
print(result)
# {'source': 'coingecko', 'status': 'success', 'count': 168, 'data': [...]}

# Get prices from DefiLlama (no API key needed)
result = llama_price_historical('ethereum:0x0000000000000000000000000000000000000000')
print(result)
# {'source': 'defillama', 'status': 'success', 'count': 1, 'data': [...]}
```

## Data Source Information

### Prices

- CoinGecko
    - **Documentation**: [CoinGecko API Docs (Demo)](https://docs.coingecko.com/v3.0.1/reference/authentication) (package uses Demo endpoints)
    - **API Key**: Required - [Get free Demo API key here](https://www.coingecko.com/en/api/pricing)
    - **Token identifiers**: Use CoinGecko IDs (e.g., `bitcoin`, `ethereum`, `usd-coin`)
- DefiLlama
    - **Documentation**: [DefiLlama API Docs](https://defillama.com/docs/api)
    - **API Key**: No key required, it's fully open and free
    - **Token identifiers**: Use format `chain:address` (e.g., `ethereum:0x6b175474e89094c44da98b954eedeac495271d0f` for DAI)

## API Reference

### `gecko_price_current(id, vs_currencies='usd', api_key=None)`

Get current cryptocurrency prices from CoinGecko.

**Parameters:**
- `id` (str): Single coin ID or comma-separated IDs (e.g., `'bitcoin'` or `'bitcoin,ethereum'`)
- `vs_currencies` (str, optional): Currency to price against (default: `'usd'`)
- `api_key` (str, required): CoinGecko Demo API key - required for API access (default: `None`)

**Returns:**
- `dict`: Standardized response with `source`, `status`, `count`, and `data` array

**Example:**
```python
result = gecko_price_current('bitcoin,ethereum', api_key='your-api-key-here')
# Returns: {'source': 'coingecko', 'status': 'success', 'count': 2, 
#           'data': [{'coin_id': 'bitcoin', 'price': 45000, 'currency': 'usd'}, ...]}
```

### `gecko_price_historical(id, vs_currency='usd', days='max', api_key=None)`

Get historical price data from CoinGecko.

**Parameters:**
- `id` (str): CoinGecko coin ID (e.g., `'ethereum'`)
- `vs_currency` (str, optional): Currency to price against (default: `'usd'`)
- `days` (int or str, optional): Days of history (`1-90` for hourly, `>90` for daily, or `'max'`)
- `api_key` (str, required): CoinGecko Demo API key - required for API access (default: `None`)

**Returns:**
- `dict`: Standardized response with `source`, `status`, `count`, and `data` array of timestamps/prices

**Example:**
```python
result = gecko_price_historical('ethereum', days=7, api_key='your-api-key-here')
# Returns: {'source': 'coingecko', 'status': 'success', 'count': 168,
#           'data': [{'timestamp': 1640908800, 'price': 2341.56}, ...]}
```

### `llama_price_historical(id, timestamp=None)`

Get historical/current prices from DefiLlama.

**Parameters:**
- `id` (str): DefiLlama ID in format `chain:address` or comma-separated IDs
- `timestamp` (int, optional): UNIX timestamp for historical prices (default: current time)

**Returns:**
- `dict`: Standardized response with `source`, `status`, `count`, and `data` array with token details

**Example:**
```python
result = llama_price_historical('ethereum:0x0000000000000000000000000000000000000000')
# Returns: {'source': 'defillama', 'status': 'success', 'count': 1,
#           'data': [{'coin_id': 'ethereum:0x00...', 'symbol': 'ETH', 'price': 2500, ...}]}
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

All functions return a standardized dictionary with `status: "error"` on failure. Check the `status` field to determine success. Common errors:
- Invalid coin IDs
- Network issues
- API rate limits
- Malformed responses

## Requirements

- Python ≥ 3.7
- requests ≥ 2.25.0

## Changelog

Can be found in the CHANGELOG.md file.

## License

MIT

## References

- [defi](https://github.com/gauss314/defi) - DeFi tools by gauss314
- [ctc](https://github.com/fei-protocol/checkthechain) - Ethereum data analysis
- [defi-protocols](https://github.com/KarpatkeyDAO/defi-protocols) - Python library by Karpatkey
