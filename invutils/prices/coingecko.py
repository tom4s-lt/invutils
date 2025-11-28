"""CoinGecko API functions for cryptocurrency price data."""

import logging
import time
from typing import Dict, Any, Union, Optional

import requests

from ..config import COINGECKO_ENDPOINTS, DEFAULT_TIMEOUT
from ..utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)


def gecko_price_current(id_gecko: str, vs_currencies: str = 'usd', api_key: Optional[str] = None) -> Dict[str, Any]:
  """
  CoinGecko - Get current price of coin or coins.
  
  Args:
    id_gecko (str): CoinGecko ID(s) - single ('bitcoin') or multiple ('bitcoin,ethereum')
    vs_currencies (str, optional): Currency(ies) to price against (default: 'usd')
    api_key (str, optional): CoinGecko Demo API key
        
  Returns:
    Dict with standardized format:
      {
        "source": "coingecko",
        "fetched_at": 1640995200,
        "status": "success" | "error",
        "count": 2,
        "data": [
          {"coin_id": "bitcoin", "price": 45000.0, "currency": "usd"},
          ...
        ]
      }
  """

  # Input validation
  if not isinstance(id_gecko, str):
    raise TypeError(f'id_gecko must be a string, got {type(id_gecko).__name__}')
  if not id_gecko.strip():
    raise ValueError('id_gecko cannot be empty or whitespace')
  
  if not isinstance(vs_currencies, str):
    raise TypeError(f'vs_currencies must be a string, got {type(vs_currencies).__name__}')
  if not vs_currencies.strip():
    raise ValueError('vs_currencies cannot be empty or whitespace')

  url = COINGECKO_ENDPOINTS['price_current']
  
  # Add API key to headers if provided
  headers = {}
  if api_key:
    headers['x-cg-demo-api-key'] = api_key
  
  # Make request with error handling
  raw_result = handle_api_request(
    'CoinGecko',
    lambda: requests.get(url, params={'ids': id_gecko, 'vs_currencies': vs_currencies}, 
                        headers=headers, timeout=DEFAULT_TIMEOUT),
    DEFAULT_TIMEOUT
  )
  
  # Build standardized response
  fetched_at = int(time.time())
  
  if raw_result is None:
    return {
      "source": "coingecko",
      "fetched_at": fetched_at,
      "status": "error",
      "count": 0,
      "data": []
    }
  
  # Transform raw API response to standard format
  data = []
  currencies_list = vs_currencies.split(',')
  
  for coin_id, price_data in raw_result.items():
    for currency in currencies_list:
      if currency in price_data:
        data.append({
          "coin_id": coin_id,
          "price": price_data[currency],
          "currency": currency
        })
  
  return {
    "source": "coingecko",
    "fetched_at": fetched_at,
    "status": "success" if data else "error",
    "count": len(data),
    "data": data
  }


def gecko_price_hist(id_gecko: str, vs_currency: str = 'usd', days: Union[int, str] = 'max', api_key: Optional[str] = None) -> Dict[str, Any]:
  """
  CoinGecko - Get historical price data for a coin.

  Args:
    id_gecko (str): CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
    vs_currency (str, optional): Currency to price against (default: 'usd')
    days (int | str, optional): Number of days or 'max' (1-90: hourly, >90: daily)
    api_key (str, optional): CoinGecko Demo API key
  
  Returns:
    Dict with standardized format:
      {
        "source": "coingecko",
        "fetched_at": 1640995200,
        "status": "success" | "error",
        "coin_id": "bitcoin",
        "currency": "usd",
        "period": {"days": 30},
        "count": 720,
        "data": [
          {"timestamp": 1640908800, "price": 44500.0},
          ...
        ]
      }
  """

  # Input validation
  if not isinstance(id_gecko, str):
    raise TypeError(f'id_gecko must be a string, got {type(id_gecko).__name__}')
  if not id_gecko.strip():
    raise ValueError('id_gecko cannot be empty or whitespace')
  
  if not isinstance(vs_currency, str):
    raise TypeError(f'vs_currency must be a string, got {type(vs_currency).__name__}')
  if not vs_currency.strip():
    raise ValueError('vs_currency cannot be empty or whitespace')
  
  if not isinstance(days, (int, str)):
    raise TypeError(f'days must be an integer or string, got {type(days).__name__}')
  
  url = COINGECKO_ENDPOINTS['price_hist'] % (id_gecko)
  
  # Add API key to headers if provided
  headers = {}
  if api_key:
    headers['x-cg-demo-api-key'] = api_key
  
  # Make request with error handling
  raw_result = handle_api_request(
    'CoinGecko',
    lambda: requests.get(url, params={'vs_currency': vs_currency, 'days': days}, 
                        headers=headers, timeout=DEFAULT_TIMEOUT),
    DEFAULT_TIMEOUT
  )
  
  # Build standardized response
  fetched_at = int(time.time())
  
  if raw_result is None or 'prices' not in raw_result:
    return {
      "source": "coingecko",
      "fetched_at": fetched_at,
      "status": "error",
      "coin_id": id_gecko,
      "currency": vs_currency,
      "period": {"days": days},
      "count": 0,
      "data": []
    }
  
  # Transform raw API response to standard format
  # CoinGecko returns: [[timestamp_ms, price], ...]
  data = []
  for timestamp_ms, price in raw_result['prices']:
    data.append({
      "timestamp": int(timestamp_ms / 1000),  # Convert ms to seconds
      "price": price
    })
  
  return {
    "source": "coingecko",
    "fetched_at": fetched_at,
    "status": "success",
    "coin_id": id_gecko,
    "currency": vs_currency,
    "period": {"days": days},
    "count": len(data),
    "data": data
  }

