## Changelog

All notable changes to this project will be documented here.

### [1.3.0] - 2025-11-29

**Changed:**
- **BREAKING**: All price functions now return standardized dictionary format
- Functions return `{'source': ..., 'status': 'success'/'error', 'count': ..., 'data': [...]}` instead of raw API responses
- Error handling: Functions now return structured error responses instead of `None`

**Migration:**
- Check `result['status']` instead of `if result is not None`
- Access data via `result['data']` array instead of raw API response structure
- CoinGecko current: `result['data'][0]['price']` instead of `result['bitcoin']['usd']`
- CoinGecko history: `result['data'][0]['timestamp']` instead of `result['prices'][0][0]`
- DefiLlama: `result['data'][0]['price']` instead of `result['ethereum:0x...']['price']`

### [1.2.0] - 2025-11-28

**Changed:**
- Reorganized package structure with `prices/` submodule
- Functions now organized by API provider (`coingecko.py`, `defillama.py`)
- Deprecated `core.py` module (will be removed in 2.0.0)
- Import paths updated (backwards compatible)

**Migration:**
- Old imports still work: `from invutils import gecko_price_current`
- New imports available: `from invutils.prices.coingecko import gecko_price_current`

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
- `gecko_price_historical()` - Get historical price data from CoinGecko
- `llama_price_historical()` - Get historical/current prices from DefiLlama
- Support for multiple coins in a single request
- Configurable timeout settings
- Detailed error logging for debugging

### [1.0.0] - Initial Release

**Added:**
- Initial package structure
- Basic API integration framework