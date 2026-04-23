"""DefiLlama API functions for cryptocurrency price data."""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

from ..config import DEFAULT_TIMEOUT, DEFILLAMA_ENDPOINTS
from ..utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)

# DefiLlama rejects span > ~500 on the /chart endpoint
_CHART_MAX_SPAN = 500

# Seconds per period string for pagination offset calculation
_PERIOD_SECONDS: Dict[str, int] = {
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def llama_price_historical(id: str, timestamp: Optional[int] = None) -> Dict[str, Any]:
    """
    DefiLlama - Get historical/current price data for tokens.

    Args:
      id (str): DefiLlama ID(s) - single ('chain:address') or multiple (comma-separated)
      timestamp (Optional[int]): UNIX timestamp for historical prices (default: current time)

    Returns:
      Dict with standardized format:
        {
          "source": "defillama",
          "fetched_at": 1640995200,
          "status": "success" | "error",
          "requested_timestamp": 1640908800,
          "count": 2,
          "data": [
            {
              "coin_id": "ethereum:0x...",
              "symbol": "ETH",
              "price": 2500.0,
              "timestamp": 1640908800,
              "confidence": 0.99
            },
            ...
          ]
        }
    """

    # Input validation
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, got {type(id).__name__}")
    if not id.strip():
        raise ValueError("id cannot be empty or whitespace")

    # Use current time if timestamp not provided
    if timestamp is None:
        timestamp = int(time.time())

    if not isinstance(timestamp, int):
        raise TypeError(f"timestamp must be an integer, got {type(timestamp).__name__}")
    if timestamp <= 0:
        raise ValueError(f"timestamp must be positive, got {timestamp}")

    url = DEFILLAMA_ENDPOINTS["price_historical"] % (timestamp, id)

    # Make request with error handling
    raw_result = handle_api_request(
        "defillama", lambda: requests.get(url, timeout=DEFAULT_TIMEOUT), DEFAULT_TIMEOUT
    )

    # Build standardized response
    fetched_at = int(time.time())

    # Check if result is valid and has 'coins' key
    if raw_result is None or "coins" not in raw_result:
        return {
            "source": "defillama",
            "fetched_at": fetched_at,
            "status": "error",
            "requested_timestamp": timestamp,
            "count": 0,
            "data": [],
        }

    # Transform raw API response to standard format
    # DefiLlama returns: {'chain:address': {'symbol': ..., 'price': ..., ...}}
    data = []
    for coin_id, coin_data in raw_result["coins"].items():
        data.append(
            {
                "coin_id": coin_id,
                "symbol": coin_data.get("symbol", "UNKNOWN"),
                "price": coin_data.get("price"),
                "timestamp": coin_data.get("timestamp", timestamp),
                "confidence": coin_data.get("confidence", None),
                "decimals": coin_data.get("decimals", None),
            }
        )

    return {
        "source": "defillama",
        "fetched_at": fetched_at,
        "status": "success" if data else "error",
        "requested_timestamp": timestamp,
        "count": len(data),
        "data": data,
    }


def _fetch_chart_chunks(
    coin_id: str, start: int, span: int, period: str, period_seconds: int
) -> List[Dict[str, Any]]:
    """Fetch all paginated chunks for a single coin_id from the /chart endpoint."""
    url = DEFILLAMA_ENDPOINTS["price_chart"] % coin_id
    points: List[Dict[str, Any]] = []
    remaining = span
    chunk_start = start

    while remaining > 0:
        chunk_span = min(remaining, _CHART_MAX_SPAN)

        raw_result = handle_api_request(
            "defillama",
            lambda u=url, s=chunk_start, n=chunk_span, p=period: requests.get(
                u,
                params={"start": s, "span": n, "period": p},
                timeout=DEFAULT_TIMEOUT,
            ),
            DEFAULT_TIMEOUT,
        )

        if raw_result is not None and "coins" in raw_result:
            points.extend(raw_result["coins"].get(coin_id, {}).get("prices", []))

        remaining -= chunk_span
        chunk_start += chunk_span * period_seconds

    return points


def llama_price_chart(
    id: str,
    start: int,
    span: int,
    period: str = "1d",
    fallback_chain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    DefiLlama - Get a historical price time series for a single token.

    Uses the /chart endpoint which returns a full time series in one call,
    unlike /prices/historical which requires one call per timestamp.
    Automatically paginates when span > 500 (API hard limit).

    If the primary ID returns no data, retries once with a substituted chain prefix
    when fallback_chain is provided. Useful when a token's canonical DefiLlama ID
    uses a different chain than where the token actually trades (e.g. ARB indexed
    under 'ethereum:0x...' but priced on 'arbitrum:0x...').

    Args:
      id (str): DefiLlama ID in 'chain:address' format (e.g., 'ethereum:0x...')
      start (int): UNIX timestamp for the start of the range
      span (int): Total number of data points to request
      period (str): Granularity — one of '5m', '15m', '30m', '1h', '4h', '1d' (default: '1d')
      fallback_chain (str, optional): Chain prefix to try if the primary ID returns empty
        (e.g., 'arbitrum'). The address part of id is reused. No-op if id has no ':'.

    Returns:
      Dict with standardized format:
        {
          "source": "defillama",
          "fetched_at": 1640995200,
          "status": "success" | "error",
          "coin_id": "ethereum:0x...",   # may reflect the fallback ID if fallback was used
          "start": 1609459200,
          "span": 365,
          "period": "1d",
          "count": 365,
          "data": [
            {"timestamp": 1609459200, "price": 730.0},
            ...
          ]
        }
    """

    # Input validation
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, got {type(id).__name__}")
    if not id.strip():
        raise ValueError("id cannot be empty or whitespace")

    if not isinstance(start, int):
        raise TypeError(f"start must be an integer, got {type(start).__name__}")
    if start <= 0:
        raise ValueError(f"start must be positive, got {start}")

    if not isinstance(span, int):
        raise TypeError(f"span must be an integer, got {type(span).__name__}")
    if span <= 0:
        raise ValueError(f"span must be positive, got {span}")

    if not isinstance(period, str):
        raise TypeError(f"period must be a string, got {type(period).__name__}")
    if period not in _PERIOD_SECONDS:
        raise ValueError(f"period must be one of {list(_PERIOD_SECONDS)}, got '{period}'")

    if fallback_chain is not None:
        if not isinstance(fallback_chain, str):
            raise TypeError(f"fallback_chain must be a string, got {type(fallback_chain).__name__}")
        if not fallback_chain.strip():
            raise ValueError("fallback_chain cannot be empty or whitespace")

    period_seconds = _PERIOD_SECONDS[period]
    all_points = _fetch_chart_chunks(id, start, span, period, period_seconds)
    effective_id = id

    # Fallback: retry once with an alternate chain prefix if primary returned nothing
    if not all_points and fallback_chain is not None and ":" in id:
        address = id.split(":", 1)[1]
        alt_id = f"{fallback_chain}:{address}"
        if alt_id != id:
            logger.info("defillama chart: %s returned empty, retrying with %s", id, alt_id)
            alt_points = _fetch_chart_chunks(alt_id, start, span, period, period_seconds)
            if alt_points:
                all_points = alt_points
                effective_id = alt_id

    fetched_at = int(time.time())

    if not all_points:
        return {
            "source": "defillama",
            "fetched_at": fetched_at,
            "status": "error",
            "coin_id": effective_id,
            "start": start,
            "span": span,
            "period": period,
            "count": 0,
            "data": [],
        }

    data = [{"timestamp": int(p["timestamp"]), "price": p["price"]} for p in all_points]

    return {
        "source": "defillama",
        "fetched_at": fetched_at,
        "status": "success",
        "coin_id": effective_id,
        "start": start,
        "span": span,
        "period": period,
        "count": len(data),
        "data": data,
    }
