"""
invutils - Tools for handling investing data.
"""

__version__ = "1.8.0"
__author__ = "Tom4s"
__email__ = "tom4s.rr@gmail.com"

# Import main functions from organized modules
from .prices import (
    gecko_price_chart,
    gecko_price_current,
    gecko_price_historical,  # back-compat alias for gecko_price_chart
    llama_price_chart,
    llama_price_historical,
    twelvedata_price_chart,  # alias for twelvedata_price_historical
    twelvedata_price_current,
    twelvedata_price_historical,
)

# Define public API
__all__ = [
    "gecko_price_chart",
    "gecko_price_current",
    "gecko_price_historical",
    "llama_price_chart",
    "llama_price_historical",
    "twelvedata_price_chart",
    "twelvedata_price_current",
    "twelvedata_price_historical",
]
