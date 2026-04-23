# invutils — API Reference

All public functions return a standardized response envelope:

```python
{
    "source": str,          # provider name
    "fetched_at": int,      # UNIX timestamp of the fetch
    "status": "success" | "error",
    "count": int,           # length of data array
    "data": list[dict],     # provider-specific records
}
```

Historical and chart functions add extra top-level keys (`coin_id`, `symbol`, `interval`, etc.) — documented per function below.

On failure, `status` is `"error"`, `count` is `0`, and `data` is `[]`. No exceptions are raised for network or API errors.

---

## CoinGecko

### `gecko_price_current(id, vs_currencies='usd', api_key=None)`

Get current prices for one or more coins.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `id` | str | — | Single coin ID or comma-separated IDs (e.g. `'bitcoin'`, `'bitcoin,ethereum'`) |
| `vs_currencies` | str | `'usd'` | Currency or currencies to price against (e.g. `'usd,eur'`) |
| `api_key` | str | `None` | CoinGecko Demo API key |

**Data items:** `{"coin_id": str, "price": float, "currency": str}`

**Example:**

```python
result = gecko_price_current('bitcoin,ethereum', api_key='your-key')
# {'source': 'coingecko', 'status': 'success', 'count': 2,
#  'data': [{'coin_id': 'bitcoin', 'price': 45000.0, 'currency': 'usd'}, ...]}
```

---

### `gecko_price_historical(id, vs_currency='usd', days='max', api_key=None)`

Get historical close prices for a single coin. Alias: `gecko_price_chart`.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `id` | str | — | CoinGecko coin ID (e.g. `'ethereum'`) |
| `vs_currency` | str | `'usd'` | Currency to price against |
| `days` | int or str | `'max'` | Days of history — `1–90` returns hourly data, `>90` returns daily, `'max'` returns full history |
| `api_key` | str | `None` | CoinGecko Demo API key |

**Extra envelope keys:** `coin_id`, `currency`, `period` (`{"days": ...}`)

**Data items:** `{"timestamp": int, "price": float}`

**Example:**

```python
result = gecko_price_historical('ethereum', days=7, api_key='your-key')
# {'source': 'coingecko', 'status': 'success', 'coin_id': 'ethereum',
#  'currency': 'usd', 'period': {'days': 7}, 'count': 168,
#  'data': [{'timestamp': 1640908800, 'price': 2341.56}, ...]}
```

---

## DefiLlama

### `llama_price_historical(id, timestamp=None)`

Get the price of one or more tokens at a point in time (or now).

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `id` | str | — | `chain:address` ID, or multiple comma-separated (e.g. `'ethereum:0x...'`) |
| `timestamp` | int | current time | UNIX timestamp for the price lookup |

**Extra envelope keys:** `requested_timestamp`

**Data items:** `{"coin_id": str, "symbol": str, "price": float, "timestamp": int, "confidence": float, "decimals": int}`

**Example:**

```python
result = llama_price_historical('ethereum:0x0000000000000000000000000000000000000000')
# {'source': 'defillama', 'status': 'success', 'count': 1,
#  'data': [{'coin_id': 'ethereum:0x00...', 'symbol': 'ETH', 'price': 2500.0, ...}]}
```

---

### `llama_price_chart(id, start, span, period='1d', fallback_chain=None)`

Get a full historical price time series for a single token. Automatically paginates when `span > 500`. Alias: `llama_price_historical` is separate — this is the `/chart` endpoint.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `id` | str | — | DefiLlama ID in `chain:address` format |
| `start` | int | — | UNIX timestamp for the start of the range |
| `span` | int | — | Number of data points to request |
| `period` | str | `'1d'` | Granularity — one of `'5m'`, `'15m'`, `'30m'`, `'1h'`, `'4h'`, `'1d'` |
| `fallback_chain` | str | `None` | Chain prefix to retry with if the primary ID returns empty (e.g. `'arbitrum'`). The address part of `id` is reused. |

**Extra envelope keys:** `coin_id` (may reflect the fallback ID), `start`, `span`, `period`

**Data items:** `{"timestamp": int, "price": float}`

**Example:**

```python
import time
result = llama_price_chart(
    'ethereum:0x0000000000000000000000000000000000000000',
    start=int(time.time()) - 365 * 86400,
    span=365,
    fallback_chain='arbitrum',
)
# {'source': 'defillama', 'status': 'success', 'coin_id': 'ethereum:0x00...', 'count': 365,
#  'data': [{'timestamp': 1640908800, 'price': 2500.0}, ...]}
```

---

## Twelve Data

Free tier: 800 requests/day. Covers stocks, ETFs, forex pairs, and indices globally.

### `twelvedata_price_current(symbol, api_key)`

Get the latest price for a stock, ETF, forex pair, or index.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `symbol` | str | — | Ticker symbol (e.g. `'AAPL'`, `'VTI'`, `'EUR/USD'`) |
| `api_key` | str | — | Twelve Data API key (required) |

**Data items:** `{"symbol": str, "price": float}`

**Example:**

```python
result = twelvedata_price_current('AAPL', api_key='your-key')
# {'source': 'twelvedata', 'status': 'success', 'count': 1,
#  'data': [{'symbol': 'AAPL', 'price': 129.41}]}
```

---

### `twelvedata_price_historical(symbol, api_key, interval='1day', outputsize=30)`

Get historical OHLCV time series. Alias: `twelvedata_price_chart`.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `symbol` | str | — | Ticker symbol (e.g. `'AAPL'`, `'VTI'`, `'EUR/USD'`) |
| `api_key` | str | — | Twelve Data API key (required) |
| `interval` | str | `'1day'` | One of `'1min'`, `'5min'`, `'15min'`, `'30min'`, `'45min'`, `'1h'`, `'2h'`, `'4h'`, `'8h'`, `'1day'`, `'1week'`, `'1month'` |
| `outputsize` | int | `30` | Number of data points, 1–5000 |

**Extra envelope keys:** `symbol`, `interval`

**Data items:** `{"datetime": str, "open": float, "high": float, "low": float, "close": float, "volume": int}` — `volume` is omitted for instruments without volume data (e.g. forex pairs).

**Example:**

```python
result = twelvedata_price_historical('AAPL', api_key='your-key', outputsize=90)
# {'source': 'twelvedata', 'status': 'success', 'symbol': 'AAPL', 'interval': '1day',
#  'count': 90, 'data': [{'datetime': '2021-01-04', 'open': 133.52, 'high': 133.61,
#                          'low': 126.76, 'close': 129.41, 'volume': 143301887}, ...]}
```

---

## Symbol / ID formats

### CoinGecko IDs

Use the CoinGecko slug: `bitcoin`, `ethereum`, `usd-coin`, `dai`.

### DefiLlama IDs

Format: `chain:contract_address`. Native tokens use the zero address.

- ETH on Ethereum: `ethereum:0x0000000000000000000000000000000000000000`
- DAI: `ethereum:0x6b175474e89094c44da98b954eedeac495271d0f`
- BUSD on BSC: `bsc:0xe9e7cea3dedca5984780bafc599bd69add087d56`

### Twelve Data symbols

Standard exchange tickers. Use `/` for forex and crypto pairs:

- US stock: `AAPL`, `MSFT`
- ETF: `VTI`, `SPY`
- Forex: `EUR/USD`, `GBP/JPY`
- Crypto (via Twelve Data): `BTC/USD`, `ETH/USD`
