# invutils

A lightweight Python package for retrieving investment price data from CoinGecko, DefiLlama, and Twelve Data APIs.

## Features

- 🪙 Current and historical cryptocurrency prices from CoinGecko
- 📊 Historical price data from DefiLlama
- 📈 Stock, ETF, forex, and index prices from Twelve Data
- 🚀 Simple, intuitive API with standardized output format
- 🔒 Type hints and proper error handling
- 📦 Minimal dependencies

## Installation

```bash
pip install git+https://github.com/xtom4s/invutils
```

## Quick Start

```python
from invutils import (
    gecko_price_current, gecko_price_historical,
    llama_price_historical, llama_price_chart,
    twelvedata_price_current, twelvedata_price_historical,
)

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
- Twelve Data
  - **Documentation**: [Twelve Data API Docs](https://twelvedata.com/docs)
  - **API Key**: Required - [Get free API key here](https://twelvedata.com/pricing) (800 req/day on free tier)
  - **Symbol identifiers**: Standard ticker symbols (e.g., `AAPL`, `VTI`, `EUR/USD`, `BTC/USD`)

## API Reference

See **[docs/README.md](docs/README.md)** for the full reference — all functions, parameters, return shapes, and examples.

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
│   ├── test_twelvedata.py   # Tests for Twelve Data functions
│   └── test_hypothesis.py  # Property-based tests (hypothesis) + large-payload parametrized cases
└── integration/             # Integration tests (real API calls) (deferred)
```

### Setup

Install development dependencies:

```bash
pip install ".[dev]"
```

For integration tests (yet to come), create a `.env` file with your API keys:

```bash
COINGECKO_API_KEY=your_coingecko_key_here
TWELVEDATA_API_KEY=your_twelvedata_key_here
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

**Note**: Unit tests run quickly without API keys. Integration tests make real API calls and require API keys in the `.env` file.

## License

MIT

## References

- [defi](https://github.com/gauss314/defi) - DeFi tools by gauss314
- [ctc](https://github.com/fei-protocol/checkthechain) - Ethereum data analysis
- [defi-protocols](https://github.com/KarpatkeyDAO/defi-protocols) - Python library by Karpatkey

