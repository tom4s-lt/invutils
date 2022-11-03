"""Function definitions for price requests to various APIs
"""

import pandas as pd
import requests as rq
from datetime import datetime
import time


def coingecko_current_px_req(id_cg:str = 'bitcoin', vs_currencies:str = 'usd'):
  """ Get current price of coin or coins (passed as csv to url)
  Args:
    - either of these:
      - coingecko id (string): coingecko id for the desired asset/coin/token
      - coingecko ids (string): "id_cg1,id_cg2,...,id_cgN"
  Returns:
    - df (dataframe): index=id_cg & one column "price"=current price
  """
  
  url = "https://api.coingecko.com/api/v3/simple/price"
  params = {'ids': id_cg, 'vs_currencies': vs_currencies}
  res = rq.get(url, params = params)
  df = pd.DataFrame(res.json()).T
  df.columns = ['price_usd']
    
  return df


def coingecko_historical_px_req(id_cg:str =  'bitcoin', days:int = 31):
  """ Get 31 past days price of coin
  Args:
    - coingecko id (string): coingecko id for the desired asset/coin/token
    - days (int): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
  Returns:
    - df (dataframe): timeseries df containing last price for each day queued
  """
  
  url ='https://api.coingecko.com/api/v3' + f'/coins/{id_cg}/market_chart'
  res = rq.get(url, params = {'vs_currency': 'usd', 'days': days})
  assert res.status_code == 200, "API Response Problem"

  prices = res.json()['prices']
  df = pd.DataFrame(prices)
  df[0] = pd.to_datetime(df[0], unit = 'ms')
  df.columns = ['date', id_cg]
  df.set_index('date', inplace = True)
  df = df.resample('D').last()

  return df


def defillama_historical_px_req(id_llama = 'ethereum:0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', timestamp = time.mktime(datetime.now().timetuple())):
  """ Get n-days price for tokens listed in defillama
  Args:
    - either of these:
        - defillama id (str): defillama id for the desired token ('chain:address')
        - defillama ids (str): "id_llama1,id_llama2,...,id_llamaN"
        
    - days (int): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data)
  Returns:
    - df (dataframe): timeseries df containing price for tokens asked for the timestamp asked
  """

  url = f"https://coins.llama.fi/prices/historical/{timestamp}/{id_llama}"
  res = rq.get(url)
  assert res.status_code == 200, "API Response Problem"
  
  prices = res.json()['coins']
  data = []
  for asset in prices:
    data.append(
        {'ticker': prices[asset]['symbol'].lower(), 'price': prices[asset]['price'], 'timestamp': datetime.fromtimestamp(timestamp)}
    )
  
  if len(data):
    df = pd.DataFrame(data).pivot(index = 'timestamp' ,columns = 'ticker', values = 'price').resample('D').last()
  else:
    df = pd.DataFrame()

  return df