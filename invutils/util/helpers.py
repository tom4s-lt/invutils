from .constants import *

def check_chain(chain):
  
  try:
    network = chain
    return network
  
  except KeyError:
    print('Wrong Network - Either bad written or not included')
