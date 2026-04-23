"""Unit tests for invutils.prices.twelvedata module."""

from unittest.mock import patch

import pytest

from invutils.prices.twelvedata import (
    twelvedata_price_chart,
    twelvedata_price_current,
    twelvedata_price_historical,
)


class TestTwelvedataPriceCurrent:
    """Test suite for twelvedata_price_current."""

    # ==================== Input Validation ====================

    def test_invalid_symbol_type(self):
        with pytest.raises(TypeError, match="symbol must be a string"):
            twelvedata_price_current(123, "key")

    def test_empty_symbol(self):
        with pytest.raises(ValueError, match="symbol cannot be empty"):
            twelvedata_price_current("", "key")

    def test_whitespace_symbol(self):
        with pytest.raises(ValueError, match="symbol cannot be empty"):
            twelvedata_price_current("   ", "key")

    def test_invalid_api_key_type(self):
        with pytest.raises(TypeError, match="api_key must be a string"):
            twelvedata_price_current("AAPL", 12345)

    def test_empty_api_key(self):
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            twelvedata_price_current("AAPL", "")

    def test_whitespace_api_key(self):
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            twelvedata_price_current("AAPL", "   ")

    # ==================== Successful Requests ====================

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_success_returns_envelope(self, mock_handle_api, mock_twelvedata_price_current_response):
        mock_handle_api.return_value = mock_twelvedata_price_current_response

        result = twelvedata_price_current("AAPL", "test-key")

        assert result["source"] == "twelvedata"
        assert result["status"] == "success"
        assert result["count"] == 1
        assert len(result["data"]) == 1
        assert "fetched_at" in result

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_success_data_item_structure(self, mock_handle_api, mock_twelvedata_price_current_response):
        mock_handle_api.return_value = mock_twelvedata_price_current_response

        result = twelvedata_price_current("AAPL", "test-key")

        item = result["data"][0]
        assert item["symbol"] == "AAPL"
        assert item["price"] == 129.41
        assert isinstance(item["price"], float)

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_symbol_uppercased_in_data(self, mock_handle_api, mock_twelvedata_price_current_response):
        mock_handle_api.return_value = mock_twelvedata_price_current_response

        result = twelvedata_price_current("aapl", "test-key")

        assert result["data"][0]["symbol"] == "AAPL"

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_fetched_at_is_reasonable(self, mock_handle_api, mock_twelvedata_price_current_response):
        mock_handle_api.return_value = mock_twelvedata_price_current_response

        result = twelvedata_price_current("AAPL", "test-key")

        assert isinstance(result["fetched_at"], int)
        assert result["fetched_at"] > 1640000000

    # ==================== Error Handling ====================

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_api_request_failure(self, mock_handle_api):
        mock_handle_api.return_value = None

        result = twelvedata_price_current("AAPL", "test-key")

        assert result["source"] == "twelvedata"
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []
        assert "fetched_at" in result

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_application_error_response(self, mock_handle_api):
        """Twelve Data returns {"code": 400, "message": "...", "status": "error"} for bad symbols."""
        mock_handle_api.return_value = {"code": 400, "message": "symbol not found", "status": "error"}

        result = twelvedata_price_current("INVALID", "test-key")

        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_empty_response(self, mock_handle_api):
        mock_handle_api.return_value = {}

        result = twelvedata_price_current("AAPL", "test-key")

        assert result["status"] == "error"
        assert result["count"] == 0


class TestTwelvedataPriceHistorical:
    """Test suite for twelvedata_price_historical."""

    # ==================== Input Validation ====================

    def test_invalid_symbol_type(self):
        with pytest.raises(TypeError, match="symbol must be a string"):
            twelvedata_price_historical(123, "key")

    def test_empty_symbol(self):
        with pytest.raises(ValueError, match="symbol cannot be empty"):
            twelvedata_price_historical("", "key")

    def test_whitespace_symbol(self):
        with pytest.raises(ValueError, match="symbol cannot be empty"):
            twelvedata_price_historical("   ", "key")

    def test_invalid_api_key_type(self):
        with pytest.raises(TypeError, match="api_key must be a string"):
            twelvedata_price_historical("AAPL", 12345)

    def test_empty_api_key(self):
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            twelvedata_price_historical("AAPL", "")

    def test_invalid_interval_type(self):
        with pytest.raises(TypeError, match="interval must be a string"):
            twelvedata_price_historical("AAPL", "key", interval=5)

    def test_invalid_interval_value(self):
        with pytest.raises(ValueError, match="interval must be one of"):
            twelvedata_price_historical("AAPL", "key", interval="2day")

    def test_invalid_outputsize_type(self):
        with pytest.raises(TypeError, match="outputsize must be an integer"):
            twelvedata_price_historical("AAPL", "key", outputsize="30")

    def test_outputsize_too_low(self):
        with pytest.raises(ValueError, match="outputsize must be between 1 and 5000"):
            twelvedata_price_historical("AAPL", "key", outputsize=0)

    def test_outputsize_too_high(self):
        with pytest.raises(ValueError, match="outputsize must be between 1 and 5000"):
            twelvedata_price_historical("AAPL", "key", outputsize=5001)

    # ==================== Successful Requests ====================

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_success_returns_envelope(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        result = twelvedata_price_historical("AAPL", "test-key")

        assert result["source"] == "twelvedata"
        assert result["status"] == "success"
        assert result["symbol"] == "AAPL"
        assert result["interval"] == "1day"
        assert result["count"] == 3
        assert len(result["data"]) == 3
        assert "fetched_at" in result

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_success_data_item_structure(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        result = twelvedata_price_historical("AAPL", "test-key")

        item = result["data"][0]
        assert "datetime" in item
        assert "open" in item
        assert "high" in item
        assert "low" in item
        assert "close" in item
        assert "volume" in item
        assert isinstance(item["open"], float)
        assert isinstance(item["high"], float)
        assert isinstance(item["low"], float)
        assert isinstance(item["close"], float)
        assert isinstance(item["volume"], int)

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_prices_converted_from_string(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        result = twelvedata_price_historical("AAPL", "test-key")

        # Twelve Data returns prices as strings — verify they're floats in output
        assert result["data"][2]["close"] == 129.41

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_forex_response_no_volume(self, mock_handle_api, mock_twelvedata_price_historical_forex_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_forex_response

        result = twelvedata_price_historical("EUR/USD", "test-key")

        assert result["status"] == "success"
        assert result["count"] == 2
        for item in result["data"]:
            assert "volume" not in item

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_symbol_uppercased(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        result = twelvedata_price_historical("aapl", "test-key")

        assert result["symbol"] == "AAPL"

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_custom_interval_reflected_in_response(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        result = twelvedata_price_historical("AAPL", "test-key", interval="1h")

        assert result["interval"] == "1h"

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_all_valid_intervals_accepted(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        valid = ["1min", "5min", "15min", "30min", "45min", "1h", "2h", "4h", "8h", "1day", "1week", "1month"]
        for interval in valid:
            result = twelvedata_price_historical("AAPL", "test-key", interval=interval)
            assert result["status"] == "success"

    # ==================== Error Handling ====================

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_api_request_failure(self, mock_handle_api):
        mock_handle_api.return_value = None

        result = twelvedata_price_historical("AAPL", "test-key")

        assert result["source"] == "twelvedata"
        assert result["status"] == "error"
        assert result["symbol"] == "AAPL"
        assert result["interval"] == "1day"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_application_error_response(self, mock_handle_api):
        mock_handle_api.return_value = {"code": 400, "message": "symbol not found", "status": "error"}

        result = twelvedata_price_historical("INVALID", "test-key")

        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_empty_values_list(self, mock_handle_api):
        mock_handle_api.return_value = {"meta": {}, "values": [], "status": "ok"}

        result = twelvedata_price_historical("AAPL", "test-key")

        assert result["status"] == "error"
        assert result["count"] == 0

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_error_response_includes_symbol_and_interval(self, mock_handle_api):
        mock_handle_api.return_value = None

        result = twelvedata_price_historical("VTI", "test-key", interval="1week", outputsize=52)

        assert result["symbol"] == "VTI"
        assert result["interval"] == "1week"


class TestTwelvedataPriceChartAlias:
    """Verify twelvedata_price_chart is an alias for twelvedata_price_historical."""

    def test_alias_is_same_function(self):
        assert twelvedata_price_chart is twelvedata_price_historical

    @patch("invutils.prices.twelvedata.handle_api_request")
    def test_alias_returns_same_result(self, mock_handle_api, mock_twelvedata_price_historical_response):
        mock_handle_api.return_value = mock_twelvedata_price_historical_response

        via_historical = twelvedata_price_historical("AAPL", "test-key")
        via_chart = twelvedata_price_chart("AAPL", "test-key")

        assert via_historical["status"] == via_chart["status"]
        assert via_historical["count"] == via_chart["count"]
        assert via_historical["symbol"] == via_chart["symbol"]
