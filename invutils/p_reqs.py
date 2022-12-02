"""Function definitions for price requests to various APIs
"""

import requests
import pandas as pd
from datetime import datetime
import time
import base64


def cgc_current_px_req(id_cg:str, vs_currencies:str = 'usd'):
  """CoinGecko - Get current price of coin or coins (passed as csv to url)
  
  Args:
    either of these:
      coingecko id (string): coingecko id for the desired asset/coin/token
      coingecko ids (string): "id_cg1,id_cg2,...,id_cgN"
  
  Returns:
    df (dataframe): timeseries df (one row) containing current px for each asset in columns - index -> [date (%Y-%m-%d)], columns -> [id_cg], values -> [current price]
  """
  assert type(id_cg) is str, 'id_cg should be a str'
  assert type(vs_currencies) is str, 'vs_currencies should be a str'

  url = "https://api.coingecko.com/api/v3/simple/price"
  
  try:
    res = requests.get(url, params = {
      'ids': id_cg,
      'vs_currencies': vs_currencies,
      }
    )
    res.raise_for_status()
  
    df = pd.DataFrame(res.json())
    df.index = [pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))]

    return df

  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


def cgc_hist_px_req(id_cg:str, vs_currency:str = 'usd', days = 'max'):
  """CoinGecko - Get CoinGecko historicacl price data of coin.
  If bad id_cg is passed - returns HTTP error

  Args:
    coingecko id (string): coingecko id for the desired asset/coin/token
    vs_currency (string, optional)
    days (int | str:'max', optional): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
  
  Returns:
    df (dataframe): timeseries df containing last price for each day queued - index-> [date (%Y-%m-%d)], columns-> [id_cg], values -> [last price for each day]
  """
  assert type(id_cg) is str, 'id_cg should be a str'
  assert type(vs_currency) is str, 'vs_currency should be a str'
  
  url ='https://api.coingecko.com/api/v3' + f'/coins/{id_cg}/market_chart'
  
  try:
    res = requests.get(url, params = {
      'vs_currency': vs_currency,
      'days': days,
      }
    )
    res.raise_for_status()

    df = pd.DataFrame(res.json()['prices'])
    df.iloc[:,0] = pd.to_datetime(df[0], unit = 'ms')  # date comes in ms in coingecko response
    df.columns = ['date', id_cg]
    df.set_index('date', inplace = True)
    df = df.resample('D').last()  # for date format - they can come at different hours

    return df
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


def dll_hist_px_req(id_llama:str, timestamp = int(time.mktime(datetime.now().timetuple()))):
  """DefiLlama - Get n-day price for tokens listed in defillama
  If no timestamp is passed, current time is used.
  If bad id_llama is passed - returns empty json

  Args:
    either of these:
      defillama id (str): defillama id for the desired token ('chain:address')
      defillama ids (str): "id_llama1,id_llama2,...,id_llamaN"
        
    timestamp (float): UNIX timestamp of time when you want historical prices
  
  Returns:
    df (dataframe): timeseries df containing price for timestamp queued - index -> [date(%Y-%m-%d-%h-%m-%s)], columns -> [id_llama], values -> [price]
  """
  assert type(id_llama) is str, 'id_llama should be a str'
  assert type(timestamp) is int, 'timestamp should be an int representing unix timestamp'

  url = f"https://coins.llama.fi/prices/historical/{timestamp}/{id_llama}"

  try:    
    res = requests.get(url)
    
    df = pd.DataFrame(res.json()['coins']) # res.json()['prices'] can come as empty dic

    try: 
      df.loc['date'] = pd.to_datetime(timestamp, unit = 's')
      df.loc['id_llama'] = df.columns
      df = df.T.pivot(index = 'date', columns = 'id_llama', values = 'price')
    
    except ValueError as errh:
      print('ValueError:', errh)
      print('Probably because response came as an empty JSON')

    return df
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)


def zpr_current_network_px_req(credentials:str, network:str):
  """Zapper - Get current prices for all tokens supported in zapper - for a given network
  If bad credentials passed - returns HTTP error on bad auth
  If bad network is passed - returns HTTP error on bad request

  Args:
    credentials (string): zapper api_key (personal)
    network (string): desired network for token price search (e.g. ethereum, arbitrum, optimism)
  
  Returns:
    records (json): record-style json containing price, name & ticker (symbol)
  """
  assert type(credentials) is str, 'credentials should be a str'
  assert type(network) is str, 'network should be a str'
  
  credentials = credentials + ":"
  encodedBytes = base64.b64encode(credentials.encode("utf-8")) # https://www.base64encoder.io/python/
  encodedStr = str(encodedBytes, "utf-8")

  url = "https://api.zapper.fi/v2/prices"
  
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


def cmc_current_px_req(credentials:str, cmc_slug:str):
  """CoinMarketCap - Get current price of coin or coins (passed as csv to url)
  
  Args:
    either of these:
      cmc slug (string): cmc_slug for the desired asset/coin/token
      cmc slugs (string): "cmc_slug1,cmc_slug2,...,cmc_slugN"
  
  Returns:
    df (dataframe): timeseries df (one row) containing current px for each asset in columns - index -> [date (%Y-%m-%d)], columns -> [cmc_slug], values -> [current price]
  """
  assert type(credentials) is str, 'credentials should be a str'
  assert type(cmc_slug) is str, 'network should be a str'

  # Pass slugs here because in params, requests converts them to 'bitcoin%2Cethereum' and cmc api takes 'bitcoin,ethereum'
  url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?slug={cmc_slug}"

  try:
    s = requests.Session()
    s.headers.update({'X-CMC_PRO_API_KEY': credentials})

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
  
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
  
  return df
