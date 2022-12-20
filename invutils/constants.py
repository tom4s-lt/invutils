# ------------------------------------------------------------------------------
# Blockchains
# ------------------------------------------------------------------------------

ETHEREUM = 'ethereum'
POLYGON = 'polygon'
ARBITRUM = 'arbitrum'
BINANCE = 'bnb'
AVALANCHE = 'avalanche'
FANTOM = 'fantom'
OPTIMISM = 'optimism'
GNOSIS = 'xdai'
ROPSTEN = 'ropsten'
KOVAN = 'kovan'
GOERLI = 'goerli'

# ------------------------------------------------------------------------------
# Networks & Explorers
# ------------------------------------------------------------------------------

NETWORK_INFO = {
  
  ETHEREUM:               {'explorer': 'etherscan'},
  POLYGON:                {'explorer': 'polygonscan'},
  ARBITRUM:               {'explorer': 'arbiscan'},
  BINANCE:                {'explorer': 'bscscan'},
  AVALANCHE:              {'explorer': 'snowtrace'},
  FANTOM:                 {'explorer': 'ftmscan'},
  OPTIMISM:               {'explorer': 'optimistic.etherscan'},
  GNOSIS:                 {'explorer': 'gnosisscan'},
  ROPSTEN:                {},
  KOVAN:                  {},
  GOERLI:                 {},
  
}

# ------------------------------------------------------------------------------
# Explorer Endpoints
# ------------------------------------------------------------------------------

EXPLORER_ENDPOINTS = {
  
  'etherscan':              'https://api.etherscan.io/api',
  'polygonscan':            'https://api.polygonscan.com/api',
  'bscscan':                'https://api.bscscan.com/api',
  'ftmscan':                'https://api.ftmscan.com/api',
  'snowtrace':              'https://api.snowtrace.io/api',
  'arbiscan':               'https://api.arbiscan.io/api',
  'optimistic.etherscan':   'https://api-optimistic.etherscan.io/api',
  'gnosisscan':             'https://api.gnosisscan.io/api',
  
}

EXPLORER_PARAMS = {
  
  # f'?module=stats&action=tokensupply&contractaddress {contract_address} &apikey {api_key}'
  'ERC_20_TOKEN_SUPPLY':    '?module=stats&action=tokensupply&contractaddress=%s&apikey=%s',
  # f'?module=account&action=tokenbalance&contractaddress= {contract_address} &address= {address} &tag=latest&apikey= {api_key}'
  'ERC_20_TOKEN_BALANCE':   '?module=account&action=tokenbalance&contractaddress=%s&address=%s&tag=latest&apikey=%s',
  
}

# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

COINGECKO_ENDPOINTS = {
  
  'base':                   'https://api.coingecko.com/api/v3',
  'px_current':             'https://api.coingecko.com/api/v3/simple/price',
  'px_hist':                'https://api.coingecko.com/api/v3/coins/%s/market_chart',  # f'https://api.coingecko.com/api/v3/coins/{id_gecko}/market_chart'

}

DEFILLAMA_ENDPOINTS = {
    
  'px_base':                'https://coins.llama.fi',
  'px_current':             'https://coins.llama.fi/prices/current/%s',  # f'https://coins.llama.fi/prices/current/{id_llama}'
  'px_hist':                'https://coins.llama.fi/prices/historical/%s/%s',  # f'https://coins.llama.fi/prices/historical/{timestamp}/{id_llama}'
  
}

ZAPPER_ENDPOINTS = {
  
  'base':                   'https://api.zapper.fi/v2',
  'px_current':             'https://api.zapper.fi/v2/prices',

}

COINMARKETCAP_ENDPOINTS = {
  
  'base':                   'https://pro-api.coinmarketcap.com/v1',
  'px_current':             'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

}
