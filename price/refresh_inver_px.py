# import pdb
# pdb.set_trace()

"""
General
- api key manager y manager de inputs o fuentes de informacion del script
- manejo de excepciones
    - que pasa si faltan api keys
    - que pasa si falta explorer de algo que tengo en la db
    - que falle la api por alguna razon

Precios
- Poner descripciones bien a las funciones
- Mas fuentes de busqueda de precios para incluir todos los tokens - faltaria zapper nomas para tenerlo por las dudas
- Una vez incluidos todos, hacer un promedio de todas las fuentes para tener valor prom - dificil priorizar esto vs otras cosas

Balance
- Ver si para pools se puede pasar una address de tokens por separado para poder buscar aunque no este en assets db los activos de la pool
    - para pools estaria bueno conseguir shares (erc-20) - para poder tener eso automatico y comparar tambien con lo que tengo
"""

import pandas as pd
import numpy as np

import requests as rq

import time
from datetime import datetime, timedelta

import base64

from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

"""
El script sirve para buscar:

1. Precios de monedas (current price)
  API de Coingecko/Zapper/DefiLlama - DeBank no tiene tier gratis

2. Pool data para pools estilo Uni-V2 (Uniswap/Sushiswap, para Balancer u otras pools se complica y no sirve)
  Con estos datos, teniendo la cantidad de shares que se tienen de la pool, se calcula la posición

3. Datos de balances
    De cada uno de los assets a los cuales se les busca el precio
    En cada billetera que se quiera
    En este caso por buscar balances directo desde la API del explorador de bloques, hay algunos tokens/assets como Claimables o cosas stakeadas que pueden no encontrarse con el script

INPUTS

  EXTERNO
    El sheets que sirve de base de datos

  INTERNO
    1. sensitive_data_dic
    2. api_data_dic
    
OUTPUTS
    
  1. consolidacion_dic = {
    "ticker": price,
    "pool shares": shares,
    "pool token balance": balance,
    "wallet balance": balance
  }
"""

sensitive_data_dic = {
# informacion relevante pero de uso privado - contiene el urldb y urlwrite
    'input_output_urls': {
        'url_inver_db': 'https://docs.google.com/spreadsheets/d/1XvCDYlolvZ1MZ-cfvx541xOO8W1Qq9U6cDAma5IQcWs',  # Google Sheets con las bases de datos de inputs en el formato que corresponde
        'url_inver_sheet': 'https://docs.google.com/spreadsheets/d/1JXOGdaa_WTISZSbkM6rCAVlivlWdAWLoQRcWNEQ3rkg'  # Google sheets para escribir los resultados del script
    },
    'directories': {
      'asset_table': 'asset_table',  # Sheet del workbook que tiene los assets
      'pool_table': 'pool_table',  # Sheet del workbook que tiene los datos de pools
      'wallet_table': 'wallet_table',  # Sheet del workbook que tiene los datos de wallets
    },
    'api_keys': {
        'zapper': '51f7c56e-8c95-4943-bc7c-b4a986bd4646', # Zapper API Keys
        'etherscan': 'M93JAJ8V3FCH1ID6R7XWZ3EW4KZRMDGSVH',  # Explorer API keys
        'polygonscan': 'VDK4A93ZJ59EIYYM4V4GVZYIT2X1BIFPQQ',  # Explorer API keys
        'bscscan': 'FC16WHHFC359G9ISH9P7CAA2YN2WS7Q6TM',  # Explorer API keys
        'ftmscan': 'WRV1UVZD673DB7ZZHD5PKN9F6R3X2FXFE3',  # Explorer API keys
        'snowtrace': 'YQX7NJNSK85KMCJBAFPN2CRAX3BUG3DY1B',  # Explorer API keys
        'arbiscan': 'MB43XWJ4Z12WZ3FSG3UTQVCXSQG54G2XBZ',  # Explorer API keys
        'optimistic.etherscan': 'USITPHA4WX6A5A4KWF3JVEPMED3BUY33MS',  # Explorer API keys
    }
}

api_data_dic = { # Podria poner params de requests tambien aca pero puede ser mejor encapsularlos en la funcion - buena idea pero ver
# informacion relevante de las apis que se usan (puede tener tambien los params de requests armados)
  'endpoints': {
      'coingecko': 'https://api.coingecko.com/api/v3',
      'zapper': 'https://api.zapper.fi/v2',
      'etherscan': 'https://api.etherscan.io/api?',
      'polygonscan': 'https://api.polygonscan.com/api?',
      'bscscan': 'https://api.bscscan.com/api?',
      'ftmscan': 'https://api.ftmscan.com/api?',
      'snowtrace': 'https://api.snowtrace.io/api?',
      'arbiscan': 'https://api.arbiscan.io/api?',
      'optimistic.etherscan': 'https://api-optimistic.etherscan.io/api?',
    }
}

# Busqueda de las sheets del workbook que sirve como base de datos, son el input del script
# Importacion de los inputs

db = gc.open_by_url(sensitive_data_dic['input_output_urls']['url_inver_db'])

sheet = db.worksheet(sensitive_data_dic['directories']['asset_table'])
asset_data_df = pd.DataFrame(sheet.get_all_records())
asset_data_df.set_index('id', drop = True, inplace = True)

sheet = db.worksheet(sensitive_data_dic['directories']['pool_table'])
pool_data_df = pd.DataFrame(sheet.get_all_records())
pool_data_df.set_index('pool_id', drop = True, inplace = True)

sheet = db.worksheet(sensitive_data_dic['directories']['wallet_table'])
wallet_data_df = pd.DataFrame(sheet.get_all_records())
wallet_data_df.set_index('wallet_id', drop = True, inplace = True)


"""
Defniciones de funciones:
1. coingeckoHistoricalPxReq()
2. defillamaHistoricalPxReq()
"""

def coingeckoHistoricalPxReq(id_cg, days = 31):
  """ Get 31 past days price of coin
  Args:
    coingecko id (string)
    days (int): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data) - UTC time for get request
  Outputs:
    df (dataframe): timeseries df containing last price for each day queued
  """
  url = api_data_dic["endpoints"]["coingecko"] + f'/coins/{id_cg}/market_chart'
  res = rq.get(url, params = {'vs_currency': 'usd', 'days': days})
  assert res.status_code == 200, "API Response Problem"

  prices = res.json()['prices']
  df = pd.DataFrame(prices)
  df[0] = pd.to_datetime(df[0], unit = 'ms')
  df.columns = ['date', id_cg]
  df.set_index('date', inplace = True)
  df.resample('D').last()

  return df


def defillamaHistoricalPxReq(id_llama, timestamp):
  """ Get 31 past days price of coin
  Args:
    coingecko id (string)
    days (int): number of days for backwards price search (1-90 days: hourly data, above 90 days: daily data)
  Outputs:
    df (dataframe): timeseries df containing price for tokens asked for the timestamp asked
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


# COINGECKO - Px search
data = []
tickers_mapper = []
for asset in asset_data_df.loc[asset_data_df.px_search == 'coingecko'].index:
  tickers_mapper.append(asset_data_df.loc[asset, 'ticker'])
  data.append(coingeckoHistoricalPxReq(asset_data_df.loc[asset, 'coingecko_id']).resample('D').last()) # Para cada fecha queda el ultimo horario del dia UTC
  time.sleep(2)

px_result_df = pd.concat(data, axis = 1)
px_result_df.columns = tickers_mapper


# Important dates and times
now = datetime.now()
d0 = datetime.now().strftime("%Y/%m/%d")
d1 = (datetime.now() - timedelta(days = 1)).strftime("%Y/%m/%d")
d7 = (datetime.now() - timedelta(days = 7)).strftime("%Y/%m/%d")
d30 = (datetime.now() - timedelta(days = 30)).strftime("%Y/%m/%d")


# DEFILLAMA - Px search
data = []
req_string = ''
for asset in asset_data_df.loc[asset_data_df.px_search == 'defillama'].index:
  req_string += asset_data_df.loc[asset, 'defillama_id'] + ','

data.append(defillamaHistoricalPxReq(req_string, time.mktime(now.timetuple())))

for timestamp in [d1, d7, d30]:
  unix = time.mktime(datetime.strptime(timestamp, "%Y/%m/%d").timetuple()) # Convierte a unix equivalente a ese dia 00:00 hs GMT/UTC - 21hs arg del dia anterior
  data.append(defillamaHistoricalPxReq(req_string, unix))
  time.sleep(2)

px_result_df = pd.concat([px_result_df, pd.concat(data, axis = 0)], axis = 1)


# Exception handling
for asset in asset_data_df.loc[asset_data_df['anchor_value'].notna()].index:
  px_result_df[asset] = asset_data_df.loc[asset, 'anchor_value']

for asset in asset_data_df.loc[asset_data_df['anchor_asset'].notna()].index:
  px_result_df[asset_data_df.loc[asset, 'ticker']] = px_result_df[asset_data_df.loc[asset, 'anchor_asset']]


# Handling df to generate desired format and add desired attributes
px_result_df = px_result_df.loc[[d0, d1, d7, d30]].T
px_result_df.columns = ["d0", "d1", "d7", "d30"]
# Eliminar duplicados - el precio en cada network me da lo mismo, lo que quiero es para balances
px_result_df = px_result_df.loc[~px_result_df.index.duplicated()]
# Agregar categorias relevantes para levantar
categories = asset_data_df.set_index('ticker')[['cat1', 'cat2', 'cat3', 'cat4']]
categories.iloc[:,0] = categories.iloc[:,0].str.upper()
categories.iloc[:,1] = categories.iloc[:,1].str.upper()
categories.iloc[:,2] = categories.iloc[:,2].str.upper()
categories.iloc[:,3] = categories.iloc[:,3].str.upper()
px_result_df = pd.concat([px_result_df, categories.loc[~categories.index.duplicated()]], axis = 1)

# Checking 
for asset in px_result_df.index: # Para controlar cualquier cosa
    print(asset.upper() + ": " + str(px_result_df.loc[asset, 'd0']))


# Exporting results to google sheets
export_list = []
export_list.append(['ticker'] + px_result_df.columns.tolist())
export_list.extend(px_result_df.fillna(0).reset_index().values.tolist())
wb = gc.open_by_url(sensitive_data_dic['input_output_urls']['url_inver_sheet'])
sheet = wb.worksheet('px_input')
sheet.update("A1", export_list) # Puede ser que no tenga que usar values
