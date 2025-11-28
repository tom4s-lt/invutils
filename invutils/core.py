"""Function definitions for price requests to various APIs."""

import logging
from datetime import datetime
import time
from typing import Dict, Any, Union, Optional

import requests
import pandas as pd

from .config import (
    COINGECKO_ENDPOINTS,
    DEFILLAMA_ENDPOINTS,
    DEFAULT_TIMEOUT
)
from .utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)

# ==============================================
# Coingecko
# ==============================================

def gecko_price_current(id_gecko: str, vs_currencies: str = 'usd', api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
  """
  CoinGecko - Get current price of coin or coins (coins passed as csv to url)
  
  Args:
    id_gecko (str): either of the following
      coingecko id for the desired asset/coin/token
      many ids for group search: "id_gecko1,id_gecko1,...,id_geckoN"
    vs_currencies (str, optional)
    api_key (str, optional): CoinGecko Demo API key
        
  Returns:
    Optional[Dict]: {'bitcoin': {'currency': price}, {'ethereum': {'currency': price}}, ...}
      Returns None on error
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
  return handle_api_request(
    'CoinGecko',
    lambda: requests.get(url, params={'ids': id_gecko, 'vs_currencies': vs_currencies}, 
                        headers=headers, timeout=DEFAULT_TIMEOUT),
    DEFAULT_TIMEOUT
  )


def gecko_price_hist(id_gecko: str, vs_currency: str = 'usd', days: Union[int, str] = 'max', api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
  """
  CoinGecko - Get CoinGecko historical price data of coin.
  If bad id_gecko is passed - returns HTTP error

  Args:
    id_gecko (str): coingecko id for the desired asset/coin/token
    vs_currency (str, optional)
    days (int | str:'max', optional): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
    api_key (str, optional): CoinGecko Demo API key
  
  Returns:
    Optional[Dict]: {'prices': [[date(ms), price], [date(ms), price], ...]}
      Returns None on error
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
  return handle_api_request(
    'CoinGecko',
    lambda: requests.get(url, params={'vs_currency': vs_currency, 'days': days}, 
                        headers=headers, timeout=DEFAULT_TIMEOUT),
    DEFAULT_TIMEOUT
  )

# ==============================================
# DefiLlama
# ==============================================

def llama_price_hist(id_llama: str, timestamp: Optional[int] = None) -> Optional[Dict[str, Any]]:
  """
  DefiLlama - Get n-day price for tokens listed in defillama
  If no timestamp is passed, current time is used.
  If bad id_llama is passed - returns empty json

  Args:
    id_llama (str): either of the following
      defillama id for the desired token ('chain:address')
      many ids for group search: "id_llama1,id_llama2,...,id_llamaN"
        
    timestamp (Optional[int]): UNIX timestamp of time when you want historical prices
      If None, uses current time
  
  Returns:
    Optional[Dict]: {defillama_id: {..., 'symbol': symbol, 'price': price}} - Has some other data
      Returns None on error
  """

  # Input validation
  if not isinstance(id_llama, str):
    raise TypeError(f'id_llama must be a string, got {type(id_llama).__name__}')
  if not id_llama.strip():
    raise ValueError('id_llama cannot be empty or whitespace')
  
  # Use current time if timestamp not provided
  if timestamp is None:
    timestamp = int(time.mktime(datetime.now().timetuple()))
  
  if not isinstance(timestamp, int):
    raise TypeError(f'timestamp must be an integer, got {type(timestamp).__name__}')
  if timestamp <= 0:
    raise ValueError(f'timestamp must be positive, got {timestamp}')
  
  url = DEFILLAMA_ENDPOINTS['price_hist'] % (timestamp, id_llama)

  # Make request with error handling
  result = handle_api_request(
    'DefiLlama',
    lambda: requests.get(url, timeout=DEFAULT_TIMEOUT),
    DEFAULT_TIMEOUT
  )
  
  # DefiLlama-specific: Extract 'coins' key from response
  if result and 'coins' in result:
    return result['coins']
  elif result:
    logger.error("DefiLlama Response Error: 'coins' key not found in response")
    return None
  
  return result