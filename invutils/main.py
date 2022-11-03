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

from .price_reqs import coingecko_current_px_req, coingecko_historical_px_req, defillama_historical_px_req
from .sensitive_info import gen_sensitive_info

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

sensitive_data_dic = gen_sensitive_info()

# Busqueda de las sheets del workbook que sirve como base de datos, son el input del script
# Importacion de los inputs

db = gc.open_by_url(sensitive_data_dic['directories']['db']['path'])

sheet = db.worksheet(sensitive_data_dic['directories']['db']['tables']['asset_table'])
asset_data_df = pd.DataFrame(sheet.get_all_records())
asset_data_df.set_index('id', drop = True, inplace = True)

sheet = db.worksheet(sensitive_data_dic['directories']['db']['tables']['pool_table'])
pool_data_df = pd.DataFrame(sheet.get_all_records())
pool_data_df.set_index('pool_id', drop = True, inplace = True)

sheet = db.worksheet(sensitive_data_dic['directories']['db']['tables']['wallet_table'])
wallet_data_df = pd.DataFrame(sheet.get_all_records())
wallet_data_df.set_index('wallet_id', drop = True, inplace = True)

########################################################################################

# COINGECKO - Px search
data = []
tickers_mapper = []
for asset in asset_data_df.loc[asset_data_df.px_search == 'coingecko'].index:
  tickers_mapper.append(asset_data_df.loc[asset, 'ticker'])
  data.append(coingecko_historical_px_req(asset_data_df.loc[asset, 'coingecko_id']).resample('D').last()) # Para cada fecha queda el ultimo horario del dia UTC
  time.sleep(5)

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

data.append(defillama_historical_px_req(req_string, time.mktime(now.timetuple())))

for timestamp in [d1, d7, d30]:
  unix = time.mktime(datetime.strptime(timestamp, "%Y/%m/%d").timetuple()) # Convierte a unix equivalente a ese dia 00:00 hs GMT/UTC - 21hs arg del dia anterior
  data.append(defillama_historical_px_req(req_string, unix))
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
wb = gc.open_by_url(sensitive_data_dic['directories']['write']['path'])
sheet = wb.worksheet(sensitive_data_dic['directories']['write']['tables']['price_table'])
sheet.update("A1", export_list) # Puede ser que no tenga que usar values
