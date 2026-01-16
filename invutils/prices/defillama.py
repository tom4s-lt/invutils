"""DefiLlama API functions for cryptocurrency price data."""

import logging
import time
from typing import Any, Dict, Optional

import requests

from ..config import DEFAULT_TIMEOUT, DEFILLAMA_ENDPOINTS
from ..utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)


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
