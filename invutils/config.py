"""Constants and configuration for invutils."""

# ==============================================
# Request Configuration
# ==============================================

DEFAULT_TIMEOUT: int = 10

# ==============================================
# API Endpoints
# ==============================================

# CoinGecko
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_ENDPOINTS = {
    "price_current": f"{COINGECKO_BASE_URL}/simple/price",
    "price_historical": f"{COINGECKO_BASE_URL}/coins/%s/market_chart",  # f'https://api.coingecko.com/api/v3/coins/{id}/market_chart'
}

# Defillama
DEFILLAMA_BASE_COINS_URL = "https://coins.llama.fi"
DEFILLAMA_ENDPOINTS = {
    "price_current": f"{DEFILLAMA_BASE_COINS_URL}/prices/current/%s",  # f'https://coins.llama.fi/prices/current/{id}'
    "price_historical": f"{DEFILLAMA_BASE_COINS_URL}/prices/historical/%s/%s",  # f'https://coins.llama.fi/prices/historical/{timestamp}/{id}'
}
