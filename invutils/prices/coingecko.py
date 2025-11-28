"""CoinGecko API functions for cryptocurrency price data."""

import logging
from typing import Dict, Any, Union, Optional

import requests

from ..config import COINGECKO_ENDPOINTS, DEFAULT_TIMEOUT
from ..utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)


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

