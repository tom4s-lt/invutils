"""Helper utilities for invutils package."""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

import requests

# Set up logger for this module
logger = logging.getLogger(__name__)


def handle_api_request(
    api_name: str, request_func: Callable[[], requests.Response]
) -> Optional[Any]:
    """
    Handle API requests with consistent error handling.

    This function wraps API requests to provide unified error handling across
    all API calls. It catches common request exceptions and logs them appropriately.

    Args:
        api_name: Name of the API for logging (e.g., 'CoinGecko', 'DefiLlama')
        request_func: Function that makes the API request and returns Response object

    Returns:
        Parsed JSON response, or None on error

    Example:
        >>> result = handle_api_request(
        ...     'CoinGecko',
        ...     lambda: requests.get(url, params=params, timeout=10),
        ... )
    """
    try:
        res = request_func()
        res.raise_for_status()
        return res.json()

    except requests.exceptions.HTTPError as e:
        # Server returned error status (400, 404, 429, 500, etc.)
        logger.error(f"{api_name} HTTP Error {e.response.status_code}: {e}")
        return None

    except ValueError as e:
        # JSON decode error (checked before RequestException: requests' JSONDecodeError is both)
        logger.error(f"{api_name} Response Error: Invalid JSON response - {e}")
        return None

    except requests.exceptions.RequestException as e:
        # Timeout, connection failure, or any other requests error
        logger.error(f"{api_name} Request Error: {e}")
        return None


def envelope(source: str, data: List[Dict[str, Any]], **extra: Any) -> Dict[str, Any]:
    """
    Build the standardized response dict shared by every public function.

    Status is "success" only when data is non-empty. Extra keys (coin_id, period, ...)
    sit between status and count.
    """
    return {
        "source": source,
        "fetched_at": int(time.time()),
        "status": "success" if data else "error",
        **extra,
        "count": len(data),
        "data": data,
    }
