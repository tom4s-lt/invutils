def gen_sensitive_info():
  sensitive_information = {
    'directories': {
      'db': {
        'path': 'https://docs.google.com/spreadsheets/d/1XvCDYlolvZ1MZ-cfvx541xOO8W1Qq9U6cDAma5IQcWs',
        'tables': {
          'asset_table': 'asset_table', # Sheet del workbook que tiene los datos de assets
          'pool_table': 'pool_table', # Sheet del workbook que tiene los datos de pools
          'wallet_table': 'wallet_table', # Sheet del workbook que tiene los datos de wallets
        }
      },
      'write': {
        'path': 'https://docs.google.com/spreadsheets/d/1JXOGdaa_WTISZSbkM6rCAVlivlWdAWLoQRcWNEQ3rkg',
        'tables': {
          'price_table': 'px_input'
        }
      }
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
  
  return sensitive_information
