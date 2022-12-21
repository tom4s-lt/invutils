"""Function definitions for price requests to various APIs
"""

from .util import helpers as hl
from .constants import *

import requests
import pandas as pd
from datetime import datetime
import time
import base64


# ------------------------------------------------------------------------------
# CoinGecko
# ------------------------------------------------------------------------------

def gecko_current(id_gecko:str, vs_currencies:str = 'usd'):
  """CoinGecko - Get current price of coin or coins (coins passed as csv to url)
  
  Args:
    id_gecko (str): either of the following
      coingecko id for the desired asset/coin/token
      many ids for group search: "id_gecko1,id_gecko1,...,id_geckoN"
    vs_currencies (str, optional)
        
  Returns:
    df (DataFrame): timeseries df (one row) containing current px for each asset in columns \ 
      index -> [date (%Y-%m-%d)], columns -> [id_gecko], values -> [current price]
  """
  assert type(id_gecko) is str, 'id_gecko should be a str'
  assert type(vs_currencies) is str, 'vs_currencies should be a str'

  url = COINGECKO_ENDPOINTS['px_current']
  
  try:
    res = requests.get(url, params = {
      'ids': id_gecko,
      'vs_currencies': vs_currencies,
      }
    )
    res.raise_for_status()
  
    df = pd.DataFrame(res.json())
    df.index = [pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))]

    return df

  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


def gecko_hist(id_gecko:str, vs_currency:str = 'usd', days = 'max'):
  """CoinGecko - Get CoinGecko historicacl price data of coin.
  If bad id_gecko is passed - returns HTTP error

  Args:
    id_gecko (str): coingecko id for the desired asset/coin/token
    vs_currency (str, optional)
    days (int | str:'max', optional): number of days for backwards price search \
      (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
  
  Returns:
    df (DataFrame): timeseries df containing last price for each day queued \
      index-> [date (%Y-%m-%d)], columns-> [id_gecko], values -> [last price for each day]
  """
  assert type(id_gecko) is str, 'id_gecko should be a str'
  assert type(vs_currency) is str, 'vs_currency should be a str'
  
  url = COINGECKO_ENDPOINTS['px_hist'] % (id_gecko)
  
  try:
    res = requests.get(url, params = {
      'vs_currency': vs_currency,
      'days': days,
      }
    )
    res.raise_for_status()

    df = pd.DataFrame(res.json()['prices'])
    df.iloc[:,0] = pd.to_datetime(df[0], unit = 'ms')  # date comes in ms in coingecko response
    df.columns = ['date', id_gecko]
    df.set_index('date', inplace = True)
    df = df.resample('D').last()  # for date format - they can come at different hours

    return df
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


# ------------------------------------------------------------------------------
# DefiLlama
# ------------------------------------------------------------------------------
    
def llama_hist(id_llama:str, timestamp = int(time.mktime(datetime.now().timetuple()))):
  """DefiLlama - Get n-day price for tokens listed in defillama
  If no timestamp is passed, current time is used.
  If bad id_llama is passed - returns empty json

  Args:
    id_llama (str): either of the following
      defillama id for the desired token ('chain:address')
      many ids for group search: "id_llama1,id_llama2,...,id_llamaN"
        
    timestamp (float): UNIX timestamp of time when you want historical prices
  
  Returns:
    df (DataFrame): timeseries df containing price for timestamp queued \
      index -> [date(%Y-%m-%d)], columns -> [id_llama], values -> [price]
  """
  assert type(id_llama) is str, 'id_llama should be a str'
  assert type(timestamp) is int, 'timestamp should be an int representing unix timestamp'
  
  url = DEFILLAMA_ENDPOINTS['px_hist'] % (timestamp, id_llama)

  try:    
    res = requests.get(url)
    
    df = pd.DataFrame(res.json()['coins']) # res.json()['prices'] can come as empty dic

    try: 
      df.loc['date'] = pd.to_datetime(timestamp, unit = 's')
      df.loc['id_llama'] = df.columns
      df = df.T.pivot(index = 'date', columns = 'id_llama', values = 'price').resample('D').last()
    
    except ValueError as errh:
      print('ValueError:', errh)
      print('Probably because response came as an empty JSON')

    return df
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


# ------------------------------------------------------------------------------
# CoinMarketCap
# ------------------------------------------------------------------------------

def cmc_current(credentials:str, id_cmc:str):
  """Get current price of coin or coins (passed as csv to url)
  id_cmc can't end in ","

  Args:
    id_cmc (str): either of the following
      cmc slug for the desired token
      many ids for group search: "id_cmc1, id_cmc2, ..., id_cmcN"
  
  Returns:
    df (DataFrame): timeseries df (one row) containing current px for each asset in columns \
      index -> [date (%Y-%m-%d)], columns -> [id_cmc], values -> [current price]
  """
  assert type(credentials) is str, 'credentials should be a str'
  assert type(id_cmc) is str, 'id_cmc should be a str'

  # Pass slugs here because in params, requests converts them to 'bitcoin%2Cethereum' and cmc api takes 'bitcoin,ethereum'
  url = COINMARKETCAP_ENDPOINTS['px_current'] + f"?slug={id_cmc}"

  try:
    res = requests.get(url,
                headers = {'X-CMC_PRO_API_KEY': credentials, 'Accept': 'application/json'}
                )
    res.raise_for_status()

    df = pd.DataFrame.from_dict(res.json()['data'], orient = 'columns')
    data = []
    for label, row in df.items():
      data.append([row.loc['slug'], row.loc['quote']['USD']['price']])

    df = pd.DataFrame(data)
    df = df.set_index(0).T
    df.index = [pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))]
  
    return df
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


# ------------------------------------------------------------------------------
# Zapper
# ------------------------------------------------------------------------------

def zapper_current_network(credentials:str, network:str):
  """Zapper - Get current prices for all tokens supported in zapper - for a given network
  If bad credentials passed - returns HTTP error on bad auth
  If bad network is passed - returns HTTP error on bad request

  Args:
    credentials (str): zapper api_key (personal)
    network (str): desired zapper network id for token price search (e.g. ethereum, arbitrum, optimism)
  
  Returns:
    df (DataFrame): df containing - index -> [date(%Y-%m-%d)], \
      columns -> [address, name, symbol, coingeckoId, price, network], values -> [described in cols]
  """
  assert type(credentials) is str, 'credentials should be a str'
  assert type(network) is str, 'network should be a str'
  
  credentials = credentials + ":"
  encodedBytes = base64.b64encode(credentials.encode("utf-8")) # https://www.base64encoder.io/python/
  encodedStr = str(encodedBytes, "utf-8")

  url = ZAPPER_ENDPOINTS['px_current']
  
  try:
    res = requests.get(url,
                params = {'network': network},
                headers = {'Authorization': f"Basic {encodedStr}"}
                )
    res.raise_for_status()

    df = pd.DataFrame.from_records(res.json())
    df = df[['address', 'name', 'symbol', 'coingeckoId', 'price', 'network']]
    df.loc[:, 'date'] = pd.to_datetime(datetime.now().strftime("%Y/%m/%d"))
    df.set_index('date', inplace = True)
  
    return df

  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


# ------------------------------------------------------------------------------
# Etherscan
# ------------------------------------------------------------------------------


def exp_univ2_current(credentials:str, network:str, pool:str, subj1:str, subj2:str, pool_dec:int = 18, subj1_dec:int = 18, subj2_dec:int = 18):
  """Get current price of any lp token following uniswap v2 model
  Currently supports arbitrum only
  
  Args:
    credentials (str): explorer api key
    network (str): blockchain where the pool is located
    pool (str): address of the pool - the lp token contract address
    subj1 (str): token address of subjacent number 1
    subj2 (str): token address of subjacent number 1
    pool_dec (int): number of decimals of pool token
    subj1_dec (int): number of decimals of subj1 token
    subj2_dec (int): number of decimals of subj2 token
  
  Returns:
    df (DataFrame): timeseries df (one row) containing current px for the pool lp token \
      index -> [date (%Y-%m-%d)], columns -> ['network:pool'], values -> [current price]
  """
  assert type(credentials) is str, 'credentials should be a str'
  assert type(network) is str, 'network should be a str'
  assert type(pool) is str, 'pool address should be a str'
  assert type(subj1) is str, 'subj1 address should be a str'
  assert type(subj2) is str, 'subj2 address should be a str'
  assert type(pool_dec) is int, 'pool_dec should be a int'
  assert type(subj1_dec) is int, 'subj1_dec should be a int'
  assert type(subj2_dec) is int, 'subj2_dec should be a int'

  network = hl.check_chain(network)

  try:
    url = EXPLORER_ENDPOINTS[NETWORK_INFO[network]['explorer']]

    res = requests.get(url + EXPLORER_PARAMS['ERC_20_TOKEN_SUPPLY'] % (pool, credentials))
    
    pool_info = {}
    pool_info[pool] = {'balance': int(res.json()['result']) / 10**pool_dec} # # could be improved for use without univ2 model
    
    subj_dec = {subj1: subj1_dec, subj2: subj2_dec}
    
    subj_prices = llama_hist(f"{network}:{subj1},{network}:{subj2}")
    
    for subj in subj_dec:

      res = requests.get(url + EXPLORER_PARAMS['ERC_20_TOKEN_BALANCE'] % (subj, pool, credentials))

      pool_info[subj] = {
          'balance': int(res.json()['result']) / 10**subj_dec[subj],
          'price': subj_prices[f"{network}:{subj}"].iloc[0]
      }
    
    # This 0 is for tidiness in format
    pool_info[pool]['price'] = (0 \
    + pool_info[subj1]['balance'] * pool_info[subj1]['price'] \
    + pool_info[subj1]['balance'] * pool_info[subj1]['price']) \
    / pool_info[pool]['balance']

    current_date = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))

    df = pd.DataFrame(pool_info[pool]['price'], columns = [f"{network}:{pool}"], index = [current_date])

    return df
  
  except KeyError:
    print("Chain explorer not supported:", network)
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
