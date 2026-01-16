"""Unit tests for invutils.prices.coingecko module."""

from unittest.mock import patch

import pytest

from invutils.prices.coingecko import gecko_price_current, gecko_price_historical


class TestGeckoPriceCurrent:
    """Test suite for gecko_price_current function."""

    # ==================== Input Validation Tests ====================

    def test_invalid_id_type(self):
        """Test that non-string id raises TypeError."""
        with pytest.raises(TypeError, match="id must be a string"):
            gecko_price_current(123)

    def test_invalid_id_type_list(self):
        """Test that list id raises TypeError."""
        with pytest.raises(TypeError, match="id must be a string"):
            gecko_price_current(["bitcoin", "ethereum"])

    def test_empty_id_string(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_current("")

    def test_whitespace_id_string(self):
        """Test that whitespace-only id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_current("   ")

    def test_invalid_vs_currencies_type(self):
        """Test that non-string vs_currencies raises TypeError."""
        with pytest.raises(TypeError, match="vs_currencies must be a string"):
            gecko_price_current("bitcoin", vs_currencies=123)

    def test_empty_vs_currencies_string(self):
        """Test that empty vs_currencies raises ValueError."""
        with pytest.raises(ValueError, match="vs_currencies cannot be empty"):
            gecko_price_current("bitcoin", vs_currencies="")

    def test_whitespace_vs_currencies_string(self):
        """Test that whitespace-only vs_currencies raises ValueError."""
        with pytest.raises(ValueError, match="vs_currencies cannot be empty"):
            gecko_price_current("bitcoin", vs_currencies="  ")

    # ==================== Successful Request Tests ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_successful_single_coin(self, mock_handle_api):
        """Test successful request for single coin."""
        mock_response = {"bitcoin": {"usd": 45000.0}}
        mock_handle_api.return_value = mock_response

        result = gecko_price_current("bitcoin")

        assert result["source"] == "coingecko"
        assert result["status"] == "success"
        assert result["count"] == 1
        assert len(result["data"]) == 1
        assert result["data"][0]["coin_id"] == "bitcoin"
        assert result["data"][0]["price"] == 45000.0
        assert result["data"][0]["currency"] == "usd"
        assert "fetched_at" in result

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_successful_multiple_coins(self, mock_handle_api, mock_gecko_price_current_response):
        """Test successful request for multiple coins."""
        mock_handle_api.return_value = mock_gecko_price_current_response

        result = gecko_price_current("bitcoin,ethereum")

        assert result["source"] == "coingecko"
        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["data"]) == 2

        # Verify both coins are in the data
        coin_ids = [item["coin_id"] for item in result["data"]]
        assert "bitcoin" in coin_ids
        assert "ethereum" in coin_ids

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_successful_multiple_currencies(self, mock_handle_api):
        """Test successful request with multiple currencies."""
        mock_response = {"bitcoin": {"usd": 45000.0, "eur": 38000.0}}
        mock_handle_api.return_value = mock_response

        result = gecko_price_current("bitcoin", vs_currencies="usd,eur")

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["data"]) == 2

        # Verify both currencies are present
        currencies = [item["currency"] for item in result["data"]]
        assert "usd" in currencies
        assert "eur" in currencies

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_with_api_key(self, mock_handle_api, mock_gecko_price_current_response):
        """Test that API key is properly passed."""
        mock_handle_api.return_value = mock_gecko_price_current_response

        result = gecko_price_current("bitcoin", api_key="test_key_123")

        # Verify the function was called and returned success
        assert result["status"] == "success"
        mock_handle_api.assert_called_once()

    # ==================== Error Handling Tests ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_api_request_failure(self, mock_handle_api):
        """Test handling of API request failure."""
        mock_handle_api.return_value = None

        result = gecko_price_current("bitcoin")

        assert result["source"] == "coingecko"
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []
        assert "fetched_at" in result

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_empty_response_data(self, mock_handle_api):
        """Test handling of empty response from API."""
        mock_handle_api.return_value = {}

        result = gecko_price_current("bitcoin")

        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_missing_currency_in_response(self, mock_handle_api):
        """Test handling when requested currency is missing from response."""
        mock_response = {"bitcoin": {"eur": 38000.0}}  # Missing 'usd'
        mock_handle_api.return_value = mock_response

        result = gecko_price_current("bitcoin", vs_currencies="usd")

        # Should return error status when no matching currencies found
        assert result["status"] == "error"
        assert result["count"] == 0

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_partial_currency_match(self, mock_handle_api):
        """Test handling when only some currencies match."""
        mock_response = {"bitcoin": {"usd": 45000.0}}  # Has 'usd' but not 'eur'
        mock_handle_api.return_value = mock_response

        result = gecko_price_current("bitcoin", vs_currencies="usd,eur")

        # Should succeed with the one matching currency
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["data"][0]["currency"] == "usd"

    # ==================== Data Transformation Tests ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_data_transformation_structure(self, mock_handle_api):
        """Test that raw API response is correctly transformed."""
        mock_response = {
            "bitcoin": {"usd": 45000.0, "eur": 38000.0},
            "ethereum": {"usd": 2500.0, "eur": 2100.0},
        }
        mock_handle_api.return_value = mock_response

        result = gecko_price_current("bitcoin,ethereum", vs_currencies="usd,eur")

        # Should have 4 entries total (2 coins × 2 currencies)
        assert result["count"] == 4
        assert len(result["data"]) == 4

        # Verify structure of each data item
        for item in result["data"]:
            assert "coin_id" in item
            assert "price" in item
            assert "currency" in item
            assert isinstance(item["price"], (int, float))

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_fetched_at_timestamp(self, mock_handle_api, mock_gecko_price_current_response):
        """Test that fetched_at timestamp is included and reasonable."""
        mock_handle_api.return_value = mock_gecko_price_current_response

        result = gecko_price_current("bitcoin")

        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], int)
        assert result["fetched_at"] > 1640000000  # After 2021


class TestGeckoPriceHistorical:
    """Test suite for gecko_price_historical function."""

    # ==================== Input Validation Tests ====================

    def test_invalid_id_type(self):
        """Test that non-string id raises TypeError."""
        with pytest.raises(TypeError, match="id must be a string"):
            gecko_price_historical(123)

    def test_empty_id_string(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_historical("")

    def test_whitespace_id_string(self):
        """Test that whitespace-only id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_historical("   ")

    def test_invalid_vs_currency_type(self):
        """Test that non-string vs_currency raises TypeError."""
        with pytest.raises(TypeError, match="vs_currency must be a string"):
            gecko_price_historical("bitcoin", vs_currency=123)

    def test_empty_vs_currency_string(self):
        """Test that empty vs_currency raises ValueError."""
        with pytest.raises(ValueError, match="vs_currency cannot be empty"):
            gecko_price_historical("bitcoin", vs_currency="")

    def test_invalid_days_type(self):
        """Test that invalid days type raises TypeError."""
        with pytest.raises(TypeError, match="days must be an integer or string"):
            gecko_price_historical("bitcoin", days=["30"])

    def test_valid_days_as_int(self):
        """Test that days can be an integer."""
        with patch("invutils.prices.coingecko.handle_api_request") as mock_handle_api:
            mock_handle_api.return_value = None
            result = gecko_price_historical("bitcoin", days=30)
            # Should not raise an error, just return error response
            assert result["status"] == "error"

    def test_valid_days_as_string(self):
        """Test that days can be a string."""
        with patch("invutils.prices.coingecko.handle_api_request") as mock_handle_api:
            mock_handle_api.return_value = None
            result = gecko_price_historical("bitcoin", days="max")
            assert result["status"] == "error"

    # ==================== Successful Request Tests ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_successful_historical_request(
        self, mock_handle_api, mock_gecko_price_historical_response
    ):
        """Test successful historical price request."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin", days=30)

        assert result["source"] == "coingecko"
        assert result["status"] == "success"
        assert result["coin_id"] == "bitcoin"
        assert result["currency"] == "usd"
        assert result["period"] == {"days": 30}
        assert result["count"] == 3
        assert len(result["data"]) == 3
        assert "fetched_at" in result

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_timestamp_conversion(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test that timestamps are correctly converted from milliseconds to seconds."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin")

        # Verify timestamps are in seconds, not milliseconds
        for item in result["data"]:
            assert "timestamp" in item
            assert item["timestamp"] == 1640908800 or item["timestamp"] == 1640995200 or item["timestamp"] == 1641081600
            # Should be ~10 digits (seconds), not ~13 digits (milliseconds)
            assert item["timestamp"] < 9999999999

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_price_data_structure(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test that price data has correct structure."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin")

        for item in result["data"]:
            assert "timestamp" in item
            assert "price" in item
            assert isinstance(item["timestamp"], int)
            assert isinstance(item["price"], (int, float))
            assert len(item) == 2  # Only timestamp and price

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_with_api_key(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test that API key is properly passed."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin", api_key="test_key_456")

        assert result["status"] == "success"
        mock_handle_api.assert_called_once()

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_different_currencies(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test with different currency parameter."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin", vs_currency="eur")

        assert result["status"] == "success"
        assert result["currency"] == "eur"

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_max_days_parameter(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test with 'max' days parameter."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin", days="max")

        assert result["status"] == "success"
        assert result["period"] == {"days": "max"}

    # ==================== Error Handling Tests ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_api_request_failure(self, mock_handle_api):
        """Test handling of API request failure."""
        mock_handle_api.return_value = None

        result = gecko_price_historical("bitcoin")

        assert result["source"] == "coingecko"
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []
        assert result["coin_id"] == "bitcoin"
        assert result["currency"] == "usd"
        assert "period" in result
        assert "fetched_at" in result

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_missing_prices_key(self, mock_handle_api):
        """Test handling when 'prices' key is missing from response."""
        mock_response = {"market_caps": [], "total_volumes": []}  # Missing 'prices'
        mock_handle_api.return_value = mock_response

        result = gecko_price_historical("bitcoin")

        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_empty_prices_list(self, mock_handle_api):
        """Test handling of empty prices list."""
        mock_response = {"prices": [], "market_caps": [], "total_volumes": []}
        mock_handle_api.return_value = mock_response

        result = gecko_price_historical("bitcoin")

        # Empty data is still a success (just no data points)
        assert result["status"] == "success"
        assert result["count"] == 0
        assert result["data"] == []

    # ==================== Edge Cases ====================

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_single_data_point(self, mock_handle_api):
        """Test with single price data point."""
        mock_response = {"prices": [[1640908800000, 45000.0]]}
        mock_handle_api.return_value = mock_response

        result = gecko_price_historical("bitcoin", days=1)

        assert result["status"] == "success"
        assert result["count"] == 1
        assert len(result["data"]) == 1

    @patch("invutils.prices.coingecko.handle_api_request")
    def test_fetched_at_timestamp(self, mock_handle_api, mock_gecko_price_historical_response):
        """Test that fetched_at timestamp is included and reasonable."""
        mock_handle_api.return_value = mock_gecko_price_historical_response

        result = gecko_price_historical("bitcoin")

        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], int)
        assert result["fetched_at"] > 1640000000  # After 2021
