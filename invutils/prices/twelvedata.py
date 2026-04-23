"""Twelve Data API functions for traditional asset price data."""

import logging
import time
from typing import Any, Dict

import requests

from ..config import DEFAULT_TIMEOUT, TWELVEDATA_ENDPOINTS
from ..utils import handle_api_request

logger = logging.getLogger(__name__)

_VALID_INTERVALS = {
    "1min", "5min", "15min", "30min", "45min",
    "1h", "2h", "4h", "8h", "1day", "1week", "1month",
}


def twelvedata_price_current(symbol: str, api_key: str) -> Dict[str, Any]:
    """
    Twelve Data - Get the latest price for a stock, ETF, forex pair, or index.

    Args:
        symbol (str): Ticker symbol (e.g., 'AAPL', 'VTI', 'EUR/USD')
        api_key (str): Twelve Data API key

    Returns:
        Dict with standardized format:
            {
                "source": "twelvedata",
                "fetched_at": 1640995200,
                "status": "success" | "error",
                "count": 1,
                "data": [{"symbol": "AAPL", "price": 129.41}]
            }
    """
    if not isinstance(symbol, str):
        raise TypeError(f"symbol must be a string, got {type(symbol).__name__}")
    if not symbol.strip():
        raise ValueError("symbol cannot be empty or whitespace")

    if not isinstance(api_key, str):
        raise TypeError(f"api_key must be a string, got {type(api_key).__name__}")
    if not api_key.strip():
        raise ValueError("api_key cannot be empty or whitespace")

    raw_result = handle_api_request(
        "twelvedata",
        lambda: requests.get(
            TWELVEDATA_ENDPOINTS["price_current"],
            params={"symbol": symbol, "apikey": api_key},
            timeout=DEFAULT_TIMEOUT,
        ),
        DEFAULT_TIMEOUT,
    )

    fetched_at = int(time.time())

    if raw_result is None or "price" not in raw_result:
        return {
            "source": "twelvedata",
            "fetched_at": fetched_at,
            "status": "error",
            "count": 0,
            "data": [],
        }

    return {
        "source": "twelvedata",
        "fetched_at": fetched_at,
        "status": "success",
        "count": 1,
        "data": [{"symbol": symbol.upper(), "price": float(raw_result["price"])}],
    }


def twelvedata_price_historical(
    symbol: str,
    api_key: str,
    interval: str = "1day",
    outputsize: int = 30,
) -> Dict[str, Any]:
    """
    Twelve Data - Get historical OHLCV time series for a stock, ETF, forex pair, or index.

    Args:
        symbol (str): Ticker symbol (e.g., 'AAPL', 'VTI', 'EUR/USD')
        api_key (str): Twelve Data API key
        interval (str): Time interval — one of '1min', '5min', '15min', '30min', '45min',
            '1h', '2h', '4h', '8h', '1day', '1week', '1month' (default: '1day')
        outputsize (int): Number of data points to return, 1–5000 (default: 30)

    Returns:
        Dict with standardized format:
            {
                "source": "twelvedata",
                "fetched_at": 1640995200,
                "status": "success" | "error",
                "symbol": "AAPL",
                "interval": "1day",
                "count": 30,
                "data": [
                    {
                        "datetime": "2021-01-04",
                        "open": 133.52,
                        "high": 133.61,
                        "low": 126.76,
                        "close": 129.41,
                        "volume": 143301887   # omitted for instruments with no volume (e.g. forex)
                    },
                    ...
                ]
            }
    """
    if not isinstance(symbol, str):
        raise TypeError(f"symbol must be a string, got {type(symbol).__name__}")
    if not symbol.strip():
        raise ValueError("symbol cannot be empty or whitespace")

    if not isinstance(api_key, str):
        raise TypeError(f"api_key must be a string, got {type(api_key).__name__}")
    if not api_key.strip():
        raise ValueError("api_key cannot be empty or whitespace")

    if not isinstance(interval, str):
        raise TypeError(f"interval must be a string, got {type(interval).__name__}")
    if interval not in _VALID_INTERVALS:
        raise ValueError(f"interval must be one of {sorted(_VALID_INTERVALS)}, got '{interval}'")

    if not isinstance(outputsize, int):
        raise TypeError(f"outputsize must be an integer, got {type(outputsize).__name__}")
    if not 1 <= outputsize <= 5000:
        raise ValueError(f"outputsize must be between 1 and 5000, got {outputsize}")

    raw_result = handle_api_request(
        "twelvedata",
        lambda: requests.get(
            TWELVEDATA_ENDPOINTS["time_series"],
            params={
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": api_key,
            },
            timeout=DEFAULT_TIMEOUT,
        ),
        DEFAULT_TIMEOUT,
    )

    fetched_at = int(time.time())

    if raw_result is None or "values" not in raw_result:
        return {
            "source": "twelvedata",
            "fetched_at": fetched_at,
            "status": "error",
            "symbol": symbol.upper(),
            "interval": interval,
            "count": 0,
            "data": [],
        }

    data: list = []
    for entry in raw_result["values"]:
        row: Dict[str, Any] = {
            "datetime": entry["datetime"],
            "open": float(entry["open"]),
            "high": float(entry["high"]),
            "low": float(entry["low"]),
            "close": float(entry["close"]),
        }
        volume = entry.get("volume")
        if volume is not None:
            row["volume"] = int(volume)
        data.append(row)

    return {
        "source": "twelvedata",
        "fetched_at": fetched_at,
        "status": "success" if data else "error",
        "symbol": symbol.upper(),
        "interval": interval,
        "count": len(data),
        "data": data,
    }


# Convenience alias matching the naming pattern of other providers
twelvedata_price_chart = twelvedata_price_historical
