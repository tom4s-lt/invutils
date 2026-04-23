"""Unit tests for invutils.prices.defillama module."""

from unittest.mock import patch

import pytest

from invutils.prices.defillama import llama_price_chart, llama_price_historical


class TestLlamaPriceHistorical:
    """Test suite for llama_price_historical function."""

    # ==================== Input Validation Tests ====================

    def test_invalid_id_type(self):
        """Test that non-string id raises TypeError."""
        with pytest.raises(TypeError, match="id must be a string"):
            llama_price_historical(123)

    def test_invalid_id_type_list(self):
        """Test that list id raises TypeError."""
        with pytest.raises(TypeError, match="id must be a string"):
            llama_price_historical(["ethereum:0x0000"])

    def test_empty_id_string(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_historical("")

    def test_whitespace_id_string(self):
        """Test that whitespace-only id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_historical("   ")

    def test_invalid_timestamp_type(self):
        """Test that non-integer timestamp raises TypeError."""
        with pytest.raises(TypeError, match="timestamp must be an integer"):
            llama_price_historical("ethereum:0x0000", timestamp="1640908800")

    def test_invalid_timestamp_type_float(self):
        """Test that float timestamp raises TypeError."""
        with pytest.raises(TypeError, match="timestamp must be an integer"):
            llama_price_historical("ethereum:0x0000", timestamp=1640908800.5)

    def test_negative_timestamp(self):
        """Test that negative timestamp raises ValueError."""
        with pytest.raises(ValueError, match="timestamp must be positive"):
            llama_price_historical("ethereum:0x0000", timestamp=-100)

    def test_zero_timestamp(self):
        """Test that zero timestamp raises ValueError."""
        with pytest.raises(ValueError, match="timestamp must be positive"):
            llama_price_historical("ethereum:0x0000", timestamp=0)

    # ==================== Successful Request Tests ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_successful_single_token(self, mock_handle_api, mock_llama_price_historical_response):
        """Test successful request for single token."""
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["source"] == "defillama"
        assert result["status"] == "success"
        assert result["requested_timestamp"] == 1640908800
        assert result["count"] == 1
        assert len(result["data"]) == 1
        assert "fetched_at" in result

        # Verify data structure
        token_data = result["data"][0]
        assert token_data["coin_id"] == "ethereum:0x0000000000000000000000000000000000000000"
        assert token_data["symbol"] == "ETH"
        assert token_data["price"] == 2500.0
        assert token_data["timestamp"] == 1640908800
        assert token_data["confidence"] == 0.99
        assert token_data["decimals"] == 18

    @patch("invutils.prices.defillama.handle_api_request")
    def test_successful_multiple_tokens(self, mock_handle_api):
        """Test successful request for multiple tokens."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "symbol": "ETH",
                    "price": 2500.0,
                    "timestamp": 1640908800,
                    "confidence": 0.99,
                    "decimals": 18,
                },
                "ethereum:0x6b175474e89094c44da98b954eedeac495271d0f": {
                    "symbol": "DAI",
                    "price": 1.0,
                    "timestamp": 1640908800,
                    "confidence": 0.99,
                    "decimals": 18,
                },
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000,ethereum:0x6b175474e89094c44da98b954eedeac495271d0f",
            timestamp=1640908800,
        )

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["data"]) == 2

        # Verify both tokens are present
        symbols = [item["symbol"] for item in result["data"]]
        assert "ETH" in symbols
        assert "DAI" in symbols

    @patch("invutils.prices.defillama.handle_api_request")
    @patch("invutils.prices.defillama.time.time")
    def test_default_timestamp_uses_current_time(
        self, mock_time, mock_handle_api, mock_llama_price_historical_response
    ):
        """Test that None timestamp defaults to current time."""
        mock_time.return_value = 1650000000.5  # Returns float
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical("ethereum:0x0000000000000000000000000000000000000000")

        # Should use current time (as int)
        assert result["requested_timestamp"] == 1650000000

    @patch("invutils.prices.defillama.handle_api_request")
    def test_data_structure_complete(self, mock_handle_api, mock_llama_price_historical_response):
        """Test that all expected fields are present in data."""
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        token_data = result["data"][0]
        assert "coin_id" in token_data
        assert "symbol" in token_data
        assert "price" in token_data
        assert "timestamp" in token_data
        assert "confidence" in token_data
        assert "decimals" in token_data

    # ==================== Error Handling Tests ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_api_request_failure(self, mock_handle_api):
        """Test handling of API request failure."""
        mock_handle_api.return_value = None

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["source"] == "defillama"
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []
        assert result["requested_timestamp"] == 1640908800
        assert "fetched_at" in result

    @patch("invutils.prices.defillama.handle_api_request")
    def test_missing_coins_key(self, mock_handle_api):
        """Test handling when 'coins' key is missing from response."""
        mock_response = {"status": "success"}  # Missing 'coins'
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.defillama.handle_api_request")
    def test_empty_coins_dict(self, mock_handle_api):
        """Test handling of empty coins dictionary."""
        mock_response = {"coins": {}}
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        # Empty data should result in error status
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    # ==================== Data Transformation Tests ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_missing_optional_fields(self, mock_handle_api):
        """Test handling when optional fields are missing from coin data."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "price": 2500.0
                    # Missing symbol, timestamp, confidence, decimals
                }
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["status"] == "success"
        token_data = result["data"][0]

        # Should have defaults for missing fields
        assert token_data["symbol"] == "UNKNOWN"
        assert token_data["price"] == 2500.0
        assert token_data["timestamp"] == 1640908800  # Uses requested timestamp
        assert token_data["confidence"] is None
        assert token_data["decimals"] is None

    @patch("invutils.prices.defillama.handle_api_request")
    def test_missing_symbol_gets_default(self, mock_handle_api):
        """Test that missing symbol gets 'UNKNOWN' default."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "price": 2500.0,
                    "timestamp": 1640908800,
                }
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["data"][0]["symbol"] == "UNKNOWN"

    @patch("invutils.prices.defillama.handle_api_request")
    def test_uses_api_timestamp_when_provided(self, mock_handle_api):
        """Test that API-provided timestamp is used over requested timestamp."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "symbol": "ETH",
                    "price": 2500.0,
                    "timestamp": 1640995200,  # Different from requested
                    "confidence": 0.99,
                    "decimals": 18,
                }
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        # Should use the API's timestamp, not the requested one
        assert result["data"][0]["timestamp"] == 1640995200
        assert result["requested_timestamp"] == 1640908800

    @patch("invutils.prices.defillama.handle_api_request")
    def test_coin_id_preserved_in_output(self, mock_handle_api):
        """Test that full coin_id is preserved in output."""
        coin_id = "ethereum:0x6b175474e89094c44da98b954eedeac495271d0f"
        mock_response = {
            "coins": {coin_id: {"symbol": "DAI", "price": 1.0, "timestamp": 1640908800}}
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(coin_id, timestamp=1640908800)

        assert result["data"][0]["coin_id"] == coin_id

    # ==================== Edge Cases ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_very_old_timestamp(self, mock_handle_api, mock_llama_price_historical_response):
        """Test with very old timestamp (e.g., from 2015)."""
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1420070400
        )

        assert result["status"] == "success"
        assert result["requested_timestamp"] == 1420070400

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fetched_at_timestamp(self, mock_handle_api, mock_llama_price_historical_response):
        """Test that fetched_at timestamp is included and reasonable."""
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], int)
        assert result["fetched_at"] > 1640000000  # After 2021

    @patch("invutils.prices.defillama.handle_api_request")
    def test_zero_price(self, mock_handle_api):
        """Test handling of zero price (valid edge case)."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "symbol": "TEST",
                    "price": 0.0,
                    "timestamp": 1640908800,
                }
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["status"] == "success"
        assert result["data"][0]["price"] == 0.0

    @patch("invutils.prices.defillama.handle_api_request")
    def test_none_price(self, mock_handle_api):
        """Test handling of None price."""
        mock_response = {
            "coins": {
                "ethereum:0x0000000000000000000000000000000000000000": {
                    "symbol": "TEST",
                    "timestamp": 1640908800,
                    # price key missing, will be None from .get()
                }
            }
        }
        mock_handle_api.return_value = mock_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        assert result["status"] == "success"
        assert result["data"][0]["price"] is None

    @patch("invutils.prices.defillama.handle_api_request")
    def test_response_structure_validation(self, mock_handle_api, mock_llama_price_historical_response):
        """Test complete response structure matches expected format."""
        mock_handle_api.return_value = mock_llama_price_historical_response

        result = llama_price_historical(
            "ethereum:0x0000000000000000000000000000000000000000", timestamp=1640908800
        )

        # Verify top-level structure
        assert set(result.keys()) == {
            "source",
            "fetched_at",
            "status",
            "requested_timestamp",
            "count",
            "data",
        }

        # Verify types
        assert isinstance(result["source"], str)
        assert isinstance(result["fetched_at"], int)
        assert isinstance(result["status"], str)
        assert isinstance(result["requested_timestamp"], int)
        assert isinstance(result["count"], int)
        assert isinstance(result["data"], list)


class TestLlamaPriceChart:
    """Test suite for llama_price_chart function."""

    _COIN_ID = "ethereum:0x0000000000000000000000000000000000000000"
    _START = 1640908800
    _SPAN = 3

    # ==================== Input Validation ====================

    def test_invalid_id_type(self):
        with pytest.raises(TypeError, match="id must be a string"):
            llama_price_chart(123, start=self._START, span=self._SPAN)

    def test_empty_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_chart("", start=self._START, span=self._SPAN)

    def test_whitespace_id(self):
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_chart("   ", start=self._START, span=self._SPAN)

    def test_invalid_start_type(self):
        with pytest.raises(TypeError, match="start must be an integer"):
            llama_price_chart(self._COIN_ID, start="2022-01-01", span=self._SPAN)

    def test_invalid_start_float(self):
        with pytest.raises(TypeError, match="start must be an integer"):
            llama_price_chart(self._COIN_ID, start=1640908800.5, span=self._SPAN)

    def test_invalid_start_zero(self):
        with pytest.raises(ValueError, match="start must be positive"):
            llama_price_chart(self._COIN_ID, start=0, span=self._SPAN)

    def test_invalid_start_negative(self):
        with pytest.raises(ValueError, match="start must be positive"):
            llama_price_chart(self._COIN_ID, start=-86400, span=self._SPAN)

    def test_invalid_span_type(self):
        with pytest.raises(TypeError, match="span must be an integer"):
            llama_price_chart(self._COIN_ID, start=self._START, span="7")

    def test_invalid_span_zero(self):
        with pytest.raises(ValueError, match="span must be positive"):
            llama_price_chart(self._COIN_ID, start=self._START, span=0)

    def test_invalid_span_negative(self):
        with pytest.raises(ValueError, match="span must be positive"):
            llama_price_chart(self._COIN_ID, start=self._START, span=-1)

    def test_invalid_period_type(self):
        with pytest.raises(TypeError, match="period must be a string"):
            llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, period=86400)

    def test_invalid_period_value(self):
        with pytest.raises(ValueError, match="period must be one of"):
            llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, period="2d")

    # ==================== Successful Request ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_successful_single_chunk(self, mock_handle_api, mock_llama_price_chart_response):
        mock_handle_api.return_value = mock_llama_price_chart_response

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert result["source"] == "defillama"
        assert result["status"] == "success"
        assert result["coin_id"] == self._COIN_ID
        assert result["start"] == self._START
        assert result["span"] == self._SPAN
        assert result["period"] == "1d"
        assert result["count"] == 3
        assert len(result["data"]) == 3
        assert "fetched_at" in result
        assert isinstance(result["fetched_at"], int)

    @patch("invutils.prices.defillama.handle_api_request")
    def test_data_point_structure(self, mock_handle_api, mock_llama_price_chart_response):
        mock_handle_api.return_value = mock_llama_price_chart_response

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        for point in result["data"]:
            assert set(point.keys()) == {"timestamp", "price"}
            assert isinstance(point["timestamp"], int)

    @patch("invutils.prices.defillama.handle_api_request")
    def test_period_stored_in_response(self, mock_handle_api, mock_llama_price_chart_response):
        mock_handle_api.return_value = mock_llama_price_chart_response

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, period="1h")

        assert result["period"] == "1h"

    @patch("invutils.prices.defillama.handle_api_request")
    def test_response_envelope_keys(self, mock_handle_api, mock_llama_price_chart_response):
        mock_handle_api.return_value = mock_llama_price_chart_response

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert set(result.keys()) == {
            "source", "fetched_at", "status", "coin_id",
            "start", "span", "period", "count", "data",
        }

    # ==================== Pagination ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_pagination_calls_handle_api_twice(self, mock_handle_api, mock_llama_price_chart_response):
        # span=600 → chunk1 span=500, chunk2 span=100 → 2 calls
        mock_handle_api.return_value = mock_llama_price_chart_response

        llama_price_chart(self._COIN_ID, start=1609459200, span=600)

        assert mock_handle_api.call_count == 2

    @patch("invutils.prices.defillama.handle_api_request")
    def test_pagination_accumulates_all_points(self, mock_handle_api):
        chunk1 = {
            "coins": {
                self._COIN_ID: {
                    "prices": [
                        {"timestamp": 1609459200, "price": 730.0},
                        {"timestamp": 1609545600, "price": 740.0},
                    ]
                }
            }
        }
        chunk2 = {
            "coins": {
                self._COIN_ID: {
                    "prices": [
                        {"timestamp": 1652745600, "price": 2800.0},
                    ]
                }
            }
        }
        mock_handle_api.side_effect = [chunk1, chunk2]

        result = llama_price_chart(self._COIN_ID, start=1609459200, span=600)

        assert result["count"] == 3
        prices = [p["price"] for p in result["data"]]
        assert 730.0 in prices
        assert 2800.0 in prices

    @patch("invutils.prices.defillama.handle_api_request")
    def test_single_chunk_when_span_equals_max(self, mock_handle_api, mock_llama_price_chart_response):
        # span == 500 should be exactly one call
        mock_handle_api.return_value = mock_llama_price_chart_response

        llama_price_chart(self._COIN_ID, start=self._START, span=500)

        assert mock_handle_api.call_count == 1

    # ==================== Error Handling ====================

    @patch("invutils.prices.defillama.handle_api_request")
    def test_api_failure_returns_error(self, mock_handle_api):
        mock_handle_api.return_value = None

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert result["source"] == "defillama"
        assert result["status"] == "error"
        assert result["count"] == 0
        assert result["data"] == []

    @patch("invutils.prices.defillama.handle_api_request")
    def test_missing_coins_key(self, mock_handle_api):
        mock_handle_api.return_value = {"data": []}

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert result["status"] == "error"

    @patch("invutils.prices.defillama.handle_api_request")
    def test_coin_not_in_response(self, mock_handle_api):
        # Response has a different coin ID
        mock_handle_api.return_value = {
            "coins": {
                "bsc:0x0000000000000000000000000000000000000000": {
                    "prices": [{"timestamp": self._START, "price": 100.0}]
                }
            }
        }

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert result["status"] == "error"
        assert result["count"] == 0

    @patch("invutils.prices.defillama.handle_api_request")
    def test_empty_prices_list(self, mock_handle_api):
        mock_handle_api.return_value = {
            "coins": {self._COIN_ID: {"prices": []}}
        }

        result = llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert result["status"] == "error"

    # ==================== Fallback Chain ====================

    def test_fallback_chain_invalid_type(self):
        with pytest.raises(TypeError, match="fallback_chain must be a string"):
            llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain=123)

    def test_fallback_chain_empty_string(self):
        with pytest.raises(ValueError, match="fallback_chain cannot be empty"):
            llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="")

    def test_fallback_chain_whitespace(self):
        with pytest.raises(ValueError, match="fallback_chain cannot be empty"):
            llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="  ")

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_not_called_when_primary_succeeds(self, mock_handle_api, mock_llama_price_chart_response):
        # Primary returns data → only 1 call, no fallback
        mock_handle_api.return_value = mock_llama_price_chart_response

        result = llama_price_chart(
            self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="arbitrum"
        )

        assert mock_handle_api.call_count == 1
        assert result["status"] == "success"
        assert result["coin_id"] == self._COIN_ID

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_called_when_primary_empty(self, mock_handle_api):
        # Primary returns empty → fallback with 'arbitrum' chain. Response must use the
        # alternate coin_id as the key since that's what _fetch_chart_chunks looks up.
        alt_id = f"arbitrum:{self._COIN_ID.split(':', 1)[1]}"
        empty = {"coins": {}}
        fallback_response = {
            "coins": {
                alt_id: {
                    "prices": [
                        {"timestamp": 1640908800, "price": 2500.0},
                        {"timestamp": 1640995200, "price": 2550.0},
                        {"timestamp": 1641081600, "price": 2600.0},
                    ]
                }
            }
        }
        mock_handle_api.side_effect = [empty, fallback_response]

        result = llama_price_chart(
            self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="arbitrum"
        )

        assert mock_handle_api.call_count == 2
        assert result["status"] == "success"
        assert result["coin_id"] == alt_id

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_error_when_both_empty(self, mock_handle_api):
        # Both primary and fallback return nothing → error
        empty = {"coins": {}}
        mock_handle_api.return_value = empty

        result = llama_price_chart(
            self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="arbitrum"
        )

        assert result["status"] == "error"
        assert result["count"] == 0

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_not_attempted_when_no_colon_in_id(self, mock_handle_api):
        # id with no ':' → address cannot be split → fallback is skipped
        mock_handle_api.return_value = {"coins": {}}

        result = llama_price_chart(
            "bitcoin", start=self._START, span=self._SPAN, fallback_chain="arbitrum"
        )

        assert mock_handle_api.call_count == 1
        assert result["status"] == "error"

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_not_attempted_when_same_chain(self, mock_handle_api):
        # fallback_chain same as id's chain → alt_id == id → skip retry
        mock_handle_api.return_value = {"coins": {}}

        result = llama_price_chart(
            self._COIN_ID, start=self._START, span=self._SPAN, fallback_chain="ethereum"
        )

        assert mock_handle_api.call_count == 1
        assert result["status"] == "error"

    @patch("invutils.prices.defillama.handle_api_request")
    def test_fallback_none_does_not_retry(self, mock_handle_api):
        # Default fallback_chain=None → no second call on empty
        mock_handle_api.return_value = {"coins": {}}

        llama_price_chart(self._COIN_ID, start=self._START, span=self._SPAN)

        assert mock_handle_api.call_count == 1
