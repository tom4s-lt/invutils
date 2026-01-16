"""Unit tests for invutils.utils.helpers module."""

from unittest.mock import Mock, patch

import requests

from invutils.utils.helpers import handle_api_request


class TestHandleApiRequest:
    """Test suite for handle_api_request function."""

    def test_successful_request(self):
        """Test successful API request with valid JSON response."""
        # Create a mock response
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": [1, 2, 3]}
        mock_response.raise_for_status = (
            Mock()
        )  # No exception raised - need to use Mock() to be callable

        # Create a request function that returns the mock response
        def request_func():
            return mock_response

        # Execute
        result = handle_api_request("TestAPI", request_func, 10)

        # Assert
        assert result == {"success": True, "data": [1, 2, 3]}
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    def test_http_error_400(self):
        """Test handling of HTTP 400 Bad Request error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_http_error_404(self):
        """Test handling of HTTP 404 Not Found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_http_error_500(self):
        """Test handling of HTTP 500 Internal Server Error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_http_error_503(self):
        """Test handling of HTTP 503 Service Unavailable."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_timeout_error(self):
        """Test handling of request timeout."""

        def request_func():
            raise requests.exceptions.Timeout("Request timed out")

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_connection_error(self):
        """Test handling of connection errors."""

        def request_func():
            raise requests.exceptions.ConnectionError("Failed to connect")

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_generic_request_exception(self):
        """Test handling of generic RequestException."""

        def request_func():
            raise requests.exceptions.RequestException("Something went wrong")

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_json_decode_error(self):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_key_error(self):
        """Test handling of KeyError during response processing."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = KeyError("Missing key")

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None

    def test_empty_json_response(self):
        """Test successful handling of empty JSON object."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result == {}

    def test_nested_json_response(self):
        """Test successful handling of complex nested JSON."""
        complex_data = {
            "status": "success",
            "data": {
                "items": [{"id": 1, "value": 100}, {"id": 2, "value": 200}],
                "metadata": {"total": 2, "page": 1},
            },
        }

        mock_response = Mock()
        mock_response.json.return_value = complex_data
        mock_response.raise_for_status = Mock()

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result == complex_data
        assert result["data"]["items"][0]["value"] == 100

    @patch("invutils.utils.helpers.logger")  # perhaps over testing to have as example
    def test_logging_on_http_error(self, mock_logger):
        """Test that HTTP errors are logged correctly."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        def request_func():
            return mock_response

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None
        mock_logger.error.assert_called_once()
        # Verify the log message contains useful info
        log_call_args = str(mock_logger.error.call_args)
        assert "TestAPI" in log_call_args
        assert "404" in log_call_args

    @patch("invutils.utils.helpers.logger")
    def test_logging_on_timeout(self, mock_logger):
        """Test that timeout errors are logged with timeout value."""

        def request_func():
            raise requests.exceptions.Timeout("Request timed out")

        result = handle_api_request("TestAPI", request_func, 15)

        assert result is None
        mock_logger.error.assert_called_once()
        # Verify the log message contains the API name and timeout
        log_call_args = str(mock_logger.error.call_args)
        assert "TestAPI" in log_call_args
        assert "15" in log_call_args

    @patch("invutils.utils.helpers.logger")
    def test_logging_on_connection_error(self, mock_logger):
        """Test that connection errors are logged correctly."""

        def request_func():
            raise requests.exceptions.ConnectionError("DNS resolution failed")

        result = handle_api_request("TestAPI", request_func, 10)

        assert result is None
        mock_logger.error.assert_called_once()
        log_call_args = str(mock_logger.error.call_args)
        assert "TestAPI" in log_call_args
        assert "Connection Error" in log_call_args

    def test_different_api_names(self):
        """Test that function works with different API names."""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()

        def request_func():
            return mock_response

        # Test with different API names
        for api_name in ["CoinGecko", "DefiLlama", "CustomAPI", "Test-API-123"]:
            result = handle_api_request(api_name, request_func, 10)
            assert result == {"test": "data"}

    def test_different_timeout_values(self):
        """Test that function accepts different timeout values."""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()

        def request_func():
            return mock_response

        # Test with different timeout values
        for timeout in [1, 5, 10, 30, 60]:
            result = handle_api_request("TestAPI", request_func, timeout)
            assert result == {"test": "data"}
