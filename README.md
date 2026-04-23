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
from invutils import gecko_price_current, gecko_price_historical, llama_price_historical, llama_price_chart

# Current prices from CoinGecko (requires API key)
result = gecko_price_current('bitcoin,ethereum', api_key='your-api-key-here')
# {'source': 'coingecko', 'status': 'success', 'count': 2, 'data': [...]}

# Historical prices from CoinGecko (requires API key)
result = gecko_price_historical('ethereum', days=7, api_key='your-api-key-here')
# {'source': 'coingecko', 'status': 'success', 'count': 168, 'data': [...]}

# Price at a point in time from DefiLlama (no API key needed)
result = llama_price_historical('ethereum:0x0000000000000000000000000000000000000000')
# {'source': 'defillama', 'status': 'success', 'count': 1, 'data': [...]}

# Full daily time series from DefiLlama (auto-paginates, optional chain fallback)
import time
result = llama_price_chart(
    'ethereum:0x0000000000000000000000000000000000000000',
    start=int(time.time()) - 365 * 86400,
    span=365,
)
# {'source': 'defillama', 'status': 'success', 'coin_id': '...', 'count': 365, 'data': [...]}
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
  - **Token identifiers**: Use format `chain:address` (e.g., `ethereum:0x6b175474e89094c44da98b954eedeac495271d0f` for DAI or `ethereum:0x0000000000000000000000000000000000000000` for ETH in Ethereum - or any native token).

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

Get the price of one or more tokens at a point in time from DefiLlama.

**Parameters:**

- `id` (str): DefiLlama ID in format `chain:address`, or multiple IDs comma-separated
- `timestamp` (int, optional): UNIX timestamp (default: current time)

**Returns:**

- `dict`: Standardized response with `source`, `fetched_at`, `status`, `requested_timestamp`, `count`, and `data` array

**Example:**

```python
result = llama_price_historical('ethereum:0x0000000000000000000000000000000000000000')
# Returns: {'source': 'defillama', 'status': 'success', 'count': 1,
#           'data': [{'coin_id': 'ethereum:0x00...', 'symbol': 'ETH', 'price': 2500, ...}]}
```

---

### `llama_price_chart(id, start, span, period='1d', fallback_chain=None)`

Get a historical price time series for a single token from DefiLlama's `/chart` endpoint.
Returns the full series in one call. Automatically paginates when `span > 500`.

**Parameters:**

- `id` (str): DefiLlama ID in `chain:address` format
- `start` (int): UNIX timestamp for the start of the range
- `span` (int): Number of data points to request
- `period` (str, optional): Granularity — one of `'5m'`, `'15m'`, `'30m'`, `'1h'`, `'4h'`, `'1d'` (default: `'1d'`)
- `fallback_chain` (str, optional): Chain prefix to retry with if the primary ID returns empty (e.g. `'arbitrum'`)

**Returns:**

- `dict`: Standardized response with `source`, `fetched_at`, `status`, `coin_id`, `start`, `span`, `period`, `count`, and `data` array of `{"timestamp": int, "price": float}` dicts

**Example:**

```python
import time
result = llama_price_chart(
    'ethereum:0x0000000000000000000000000000000000000000',
    start=int(time.time()) - 365 * 86400,
    span=365,
    fallback_chain='arbitrum',
)
# Returns: {'source': 'defillama', 'status': 'success', 'coin_id': '...', 'count': 365,
#           'data': [{'timestamp': 1640908800, 'price': 2500.0}, ...]}
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

## Testing

### Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── unit/                    # Fast unit tests (mocked, no API calls)
│   ├── test_helpers.py      # Tests for utility functions
│   ├── test_coingecko.py    # Tests for CoinGecko functions
│   ├── test_defillama.py    # Tests for DefiLlama functions
│   └── test_hypothesis.py  # Property-based tests (hypothesis) + large-payload parametrized cases
└── integration/             # Integration tests (real API calls) (deferred)
```

### Setup

Install development dependencies:

```bash
pip install ".[dev]"
```

For integration tests (yet to come), create a `.env` file with your CoinGecko API key:

```bash
COINGECKO_API_KEY=your_actual_api_key_here
```

### Running Tests

```bash
# Run all unit tests (fast, no API calls)
pytest -m "not integration"

# Run all tests including integration tests
pytest

# Run with coverage report
pytest --cov=invutils --cov-report=html
```

**Note**: Unit tests run quickly without API keys. Integration tests make real API calls and require a CoinGecko API key in the `.env` file.

## License

MIT

## References

- [defi](https://github.com/gauss314/defi) - DeFi tools by gauss314
- [ctc](https://github.com/fei-protocol/checkthechain) - Ethereum data analysis
- [defi-protocols](https://github.com/KarpatkeyDAO/defi-protocols) - Python library by Karpatkey

