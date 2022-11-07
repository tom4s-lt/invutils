"""Function definitions for price requests to various APIs
"""

import pandas as pd
import requests as rq
from datetime import datetime
import time


def coingecko_current_px_req(id_cg:str = 'bitcoin', vs_currencies:str = 'usd'):
  """ Get current price of coin or coins (passed as csv to url)
  Args:
    either of these:
      coingecko id (string): coingecko id for the desired asset/coin/token
      coingecko ids (string): "id_cg1,id_cg2,...,id_cgN"
  
  Returns:
    df (dataframe): index = id_cg & one column "price" = current price - index -> [id_cg], columns -> [price], data -> [current price]
    json (json): record-style json containing id_cg & price for each asset (same information as dataframe)
  """
  
  url = "https://api.coingecko.com/api/v3/simple/price"
  params = {'ids': id_cg, 'vs_currencies': vs_currencies}
  res = rq.get(url, params = params)
  assert res.status_code == 200, "API Response Problem: " + str(res)
    
  df = pd.DataFrame(res.json()).T
  df.columns = ['price']

  json = df.reset_index()
  json.columns = ['id_cg', 'price']
  json = json.to_dict(orient = 'records')

  return df, json


def coingecko_historical_px_req(id_cg:str =  'bitcoin', days:int = 31):
  """ Get 31 past days price of coin
  Args:
    coingecko id (string): coingecko id for the desired asset/coin/token
    days (int): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
  
  Returns:
    df (dataframe): timeseries df containing last price for each day queued - index-> [date], columns-> [id_cg], data -> [last price for each day]
    json (json): record-style json containing same information as dataframe
  """
  
  url ='https://api.coingecko.com/api/v3' + f'/coins/{id_cg}/market_chart'
  res = rq.get(url, params = {'vs_currency': 'usd', 'days': days})
  assert res.status_code == 200, "API Response Problem: " + str(res)

  prices = res.json()['prices']
  df = pd.DataFrame(prices)
  df[0] = pd.to_datetime(df[0], unit = 'ms')
  df.columns = ['date', id_cg]
  df.set_index('date', inplace = True)
  df = df.resample('D').last()

  json = df.reset_index()
  json = json.to_dict(orient = 'records')

  return df, json


def defillama_historical_px_req(id_llama:str = 'ethereum:0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', timestamp = time.mktime(datetime.now().timetuple())):
  """ Get n-days price for tokens listed in defillama
  Args:
    either of these:
      defillama id (str): defillama id for the desired token ('chain:address')
      defillama ids (str): "id_llama1,id_llama2,...,id_llamaN"
        
    timestamp (float): UNIX timestamp of time when you want historical prices
  
  Returns:
    df (dataframe): timeseries df containing price for tokens asked for the timestamp asked
  """

  url = f"https://coins.llama.fi/prices/historical/{timestamp}/{id_llama}"
  res = rq.get(url)
  assert res.status_code == 200, "API Response Problem: " + str(res)
  
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


def zapper_current_network_px_req(credentials:str, network:str):
  """Get current prices for all tokens supported in zapper - for a given network
  Args:
    credentials (string): zapper api_key (personal)
    network (string): desired network for token price search (e.g. ethereum, arbitrum, optimism)
  
  Returns:
    records (json): record-style json containing price, name & ticker (symbol)
  """
  
  credentials = credentials + ":"
  encodedBytes = base64.b64encode(credentials.encode("utf-8")) # https://www.base64encoder.io/python/
  encodedStr = str(encodedBytes, "utf-8")

  url = "https://api.zapper.fi/v2/prices"
  res = rq.get(url, params = {'network': network}, headers = {'Authorization': f"Basic {encodedStr}"})
  assert res.status_code == 200, "API Response Problem: " + str(res)

  df = pd.DataFrame.from_records(res.json())
  df = df[['name', 'symbol', 'price']]
  json = df.to_dict(orient = 'records')
  
  return df, json


# def zapper_px_req(api_endpoint, api_key, token, token_address, network):
#   dic_resultados_fx = {}
#   credentials = api_key + ':'

#   encodedBytes = base64.b64encode(credentials.encode("utf-8")) # https://www.base64encoder.io/python/
#   encodedStr = str(encodedBytes, "utf-8")

#   response_prices = requests.get(
#       f"{api_endpoint}/prices/{token_address}?network={network}&timeFrame=year&currency=USD",
#       headers={'Authorization': f"Basic {encodedStr}"}
#   )

#   assert response_prices.status_code == 200, "API Response Problem"
  
#   response_prices.json()['prices']
  
#   dic_resultados_fx[token] = {
#       '0d': response_prices.json()['prices'][-1][1],
#       '1d': response_prices.json()['prices'][-3][1],
#       '7d': response_prices.json()['prices'][-9][1],
#       '30d': response_prices.json()['prices'][-32][1]
#   }

#   return dic_resultados_fx


################################################################################

# import base64
# import requests

# credentials = '51f7c56e-8c95-4943-bc7c-b4a986bd4646' + ':'

# encodedBytes = base64.b64encode(credentials.encode("utf-8")) # https://www.base64encoder.io/python/
# encodedStr = str(encodedBytes, "utf-8")
# wallet_address = '0xaef25bf5970073b39b3ec5b3d78595f12f767fd8'


# res = requests.get(
#     f"https://api.zapper.fi/v2/prices/0x4277f8F2c384827B5273592FF7CeBd9f2C1ac258?network=arbitrum&timeFrame=year&currency=USD",
#     headers={'Authorization': f"Basic {encodedStr}"})

# print(res)

# assert res.status_code == 200, "API Problem"
