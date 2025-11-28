"""DefiLlama API functions for cryptocurrency price data."""

import logging
from datetime import datetime
import time
from typing import Dict, Any, Optional

import requests

from ..config import DEFILLAMA_ENDPOINTS, DEFAULT_TIMEOUT
from ..utils import handle_api_request

# Set up logger for this module
logger = logging.getLogger(__name__)


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

