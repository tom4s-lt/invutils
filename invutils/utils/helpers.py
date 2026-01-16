"""Helper utilities for invutils package."""

import logging
from typing import Any, Callable, Dict, Optional

import requests

# Set up logger for this module
logger = logging.getLogger(__name__)


def handle_api_request(
    api_name: str,
    request_func: Callable[[],
    requests.Response], timeout: int
) -> Optional[Dict[str, Any]]:
    """
    Handle API requests with consistent error handling.

    This function wraps API requests to provide unified error handling across
    all API calls. It catches common request exceptions and logs them appropriately.

    Args:
        api_name: Name of the API for logging (e.g., 'CoinGecko', 'DefiLlama')
        request_func: Function that makes the API request and returns Response object
        timeout: Timeout value used in the request (for logging purposes)

    Returns:
        Parsed JSON response as dict, or None on error

    Example:
        >>> result = handle_api_request(
        ...     'CoinGecko',
        ...     lambda: requests.get(url, params=params, timeout=10),
        ...     10
        ... )
    """
    try:
        res = request_func()
        res.raise_for_status()
        return res.json()

    except requests.exceptions.HTTPError as e:
        # Server returned error status (400, 404, 500, etc.)
        logger.error(f"{api_name} HTTP Error {e.response.status_code}: {e}")
        return None

    except requests.exceptions.Timeout:
        # Request took longer than timeout seconds
        logger.error(f"{api_name} Timeout Error: Request took longer than {timeout}s")
        return None

    except requests.exceptions.ConnectionError as e:
        # Network problem (DNS failure, refused connection, etc.)
        logger.error(f"{api_name} Connection Error: Could not connect to API - {e}")
        return None

    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests errors
        logger.error(f"{api_name} Request Error: {e}")
        return None

    except (ValueError, KeyError) as e:
        # JSON decode error or missing expected key
        logger.error(f"{api_name} Response Error: Invalid or unexpected response format - {e}")
        return None


