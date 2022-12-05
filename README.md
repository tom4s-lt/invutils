# invutils

`invutils` is a python package with useful tools for handling investing data. It features:
- Cryptocurrency price search

It currently has limited functionality and API dependencies so as to improve git and open source skills while developing. The idea is also to make each functionality as simple as possible, without adding extra information or noise (such as adding marketcap information to prices).

Future plans include:
- Cryptocurrency balance/holdings search (for a given account)
- Yahoo finance price search for stocks

<br>

## Contents

1. [Instalation](#installation)
2. [API Dependencies](#api-dependencies)
	1. [Coingecko](#coingecko)
	2. [DefiLlama](#defillama)
	3. [Zapper](#zapper)
3. [Example Usage](#example-usage)
4. [Inspiration & References](#inspiration-&-references)

<br>

## Installation

```sh
pip install git+https://github.com/xtom4s/inverutilities.git
```

```python
from invutils import px_reqs
```

<br>

## API Dependencies

### [CoinGecko](https://www.coingecko.com/)
- [API Documentation](https://www.coingecko.com/en/api/documentation)
- Free Tier available
	- Current prices
	- Historical prices
- No key needed
- RPM limit: 10-50 calls/min
- Monthly limit: Unknown

### [DefiLlama](https://defillama.com/)
- [API Documentation](https://defillama.com/docs/api)
- Free
	- Current prices
	- Historical Prices
- No key needed
- RPM limit: not stated
- Monthly limit: Unknown

### [Zapper](https://zapper.fi/)
- [API Documentation](https://studio.zapper.fi/docs/apis/getting-started)
- Free Tier available
	- Current prices
- Key needed
- RPM Limit: Unknown
- Monthly limit: 10.000 credits/month

### [CoinMarketCap](https://coinmarketcap.com/)
- [API Documentation](https://coinmarketcap.com/api/)
- Free Tier available
	- Current prices
- Key needed
- RPM Limit: 30 calls/min
- Daily Limit: 333 credits/day
- Monthly Limit: 10.000 credits/month

<br>

## Example Usage

<br>

```python
import invutils.px_reqs as pr

df  = pr.gecko_px_req('bitcoin,ethereum,gmx,wrong_id,dai,usd-coin,cap')
print(df)
```
```text
            usd-coin   bitcoin    dai  ethereum     cap    gmx
2022-12-05  0.999788  17226.78  1.001   1286.94  313.67  54.87
```

<br>

```python
import invutils.px_reqs as pr

df  = pr.gecko_hist_px_req('ethereum')
print(df)
```
```text
               ethereum
date                   
2015-08-07     2.831620
2015-08-08     1.330750
2015-08-09          NaN
2015-08-10     0.687586
2015-08-11     1.067379
...                 ...
2022-12-01  1298.940770
2022-12-02  1276.639371
2022-12-03  1293.948023
2022-12-04  1243.040842
2022-12-05  1295.027285

[2678 rows x 1 columns]
```

<br>

```python
import invutils.px_reqs as pr

df  = pr.llama_hist_px_req('ethereum:0x0000000000000000000000000000000000000000,bsc:0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82')
print(df)
```
```text
id_llama	bsc:0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82	ethereum:0x0000000000000000000000000000000000000000
date		
2022-12-05	4.05						1287.78
```

<br>

```python
import invutils.px_reqs as pr

df  = pr.zapper_network_px_req(credentials = 'zapper-api-key', network = 'ethereum')
print(df)
```
```text
                                               address                   name	symbol       coingeckoId         price   network  
date                                                                            
2022-12-05  0x05f9abf4b0c5661e83b92c056a8791d5ccd7ca52             Joos Token	  JOOS     joos-protocol  5.646650e-07  ethereum
2022-12-05  0x1c7ede23b1361acc098a1e357c9085d131b34a01                  Shine	   SHN          shinedao  3.674210e-03  ethereum
2022-12-05  0x239119c43e3cac84c8a2d45bcba0e46f528e5f77                Dripper	  DRIP   dripper-finance  1.056790e-03  ethereum
2022-12-05  0x2688213fedd489762a281a67ae4f2295d8e17ecc            FUD finance	   FUD        fudfinance  0.000000e+00  ethereum
2022-12-05  0x26a604dffe3ddab3bee816097f81d3c4a2a4cf97  CorionX utility token	  CORX           corionx  2.357800e-04  ethereum
...                                                ...                    ...	   ...               ...           ...       ...
2022-12-05  0x932d447274dcffb4aea4f0944d3c804e88056416              Lemon Bet	  LBET         lemon-bet  1.790000e+00  ethereum
2022-12-05  0x2cc71c048a804da930e28e93f3211dc03c702995                Kripton	   LPK            l-pesa  7.807000e-05  ethereum
2022-12-05  0x9332dfc361763d58565139da819c86e773e17249                Uniplay	   UNP           uniplay  1.080420e-03  ethereum
2022-12-05  0x9b8c184439245b7bb24a5b2ec51ec81c39589e8a                  KIMEX	   KMX             kimex  1.320000e-05  ethereum
2022-12-05  0x72e203a17add19a3099137c9d7015fd3e2b7dba9       BlockchainPoland	   BCP  blockchainpoland  7.300470e-03  ethereum
```

<br>

```python
import invutils.px_reqs as pr

df = pr.cmc_current_px_req(credentials = 'cmc_api_key', cmc_slug = 'bitcoin,ethereum,bnb,multi-collateral-dai')
print(df)
```
```text
0               bitcoin     ethereum         bnb  multi-collateral-dai
2022-12-05  17093.86288  1273.398373  290.434686              0.998759
```

<br>

## Inspiration & References

- [defi](https://github.com/gauss314/defi) - DeFi open source tools from [gauss314](https://github.com/gauss314)
- [ctc](https://github.com/fei-protocol/checkthechain) - tool for collecting and analyzing data from Ethereum & EVM chains
