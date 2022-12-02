# invutils
`invutils` is a python package with useful tools for handling investing data. It features:
- Cryptocurrency price search

It currently has limited functionality and API dependencies so as to improve git and open source skills while developing. The idea is also to make each functionality as simple as possible, without adding extra information or noise (such as adding marketcap information to prices).

Future plans include:
- Cryptocurrency balance/holdings search (for a given account)
- Yahoo finance price search for stocks

## Contents
1. [Instalation](#installation)
2. [API Dependencies](#api-dependencies)
	1. [Coingecko](#coingecko)
	2. [DefiLlama](#defillama)
	3. [Zapper](#zapper)
3. Example Usage
4. [Inspiration & References](#inspiration-&-references)

## Installation

```sh
pip install git+https://github.com/xtom4s/inverutilities.git
```

## API Dependencies

### [CoinGecko](https://www.coingecko.com/)
- [API Documentation](https://www.coingecko.com/en/api/documentation)
- Free Tier available
- No key needed
- RPM limit: 10-50 calls/min
- Monthly limit: Unknown

### [DefiLlama](https://defillama.com/)
- [API Documentation](https://defillama.com/docs/api)
- Free
- No key needed
- RPM limit: not stated
- Monthly limit: Unknown

### [Zapper](https://zapper.fi/)
- [API Documentation](https://studio.zapper.fi/docs/apis/getting-started)
- Free Tier available
- Key needed
- RPM Limit: Unknown
- Monthly limit: 10.000 points

## Inspiration & References
[defi](https://github.com/gauss314/defi) - DeFi open source tools from [gauss314](https://github.com/gauss314)
[ctc](https://github.com/fei-protocol/checkthechain) - tool for collecting and analyzing data from Ethereum & EVM chains
